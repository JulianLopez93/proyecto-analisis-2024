import streamlit as st
from streamlit_agraph import Node, Edge, Config, agraph
import json
import pandas as pd
import numpy as np
import copy

# Inicializa st.session_state si aún no se ha hecho
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "edges" not in st.session_state:
    st.session_state["edges"] = []
if "previous_nodes" not in st.session_state:
    st.session_state["previous_nodes"] = []
if "previous_edges" not in st.session_state:
    st.session_state["previous_edges"] = []
if "show_json" not in st.session_state:
    st.session_state["show_json"] = False
if "json_data" not in st.session_state:  # Añade esta línea
    st.session_state["json_data"] = ""  # Añade esta línea

# Agrega un selector de archivos en la barra lateral
uploaded_file = st.sidebar.file_uploader("Elige un archivo JSON", type="json")

if uploaded_file is not None and not st.session_state["nodes"] and not st.session_state["edges"]:
    # Lee el archivo JSON
    data = json.load(uploaded_file)

    # Añade nodos y aristas a las listas
    for item in data['graph'][0]['data']:
        node = Node(id=item['id'], label=item['label'], size=item['radius'])
        st.session_state["nodes"].append(node)
        for linked_node in item['linkedTo']:
            edge = Edge(source=item['id'], target=linked_node['nodeId'], label=str(linked_node['weight']))
            st.session_state["edges"].append(edge)

# Agrega un menú desplegable en la barra lateral
option = st.sidebar.selectbox('Nodo', ['Agregar', 'Editar', 'Eliminar'])

    # Agrega, edita o elimina un nodo dependiendo de la opción seleccionada
if option == 'Agregar':
    with st.sidebar.form(key='add_node_form'):
        node_id = st.number_input('ID del nodo', value=1, step=1)
        node_label = st.text_input('Etiqueta del nodo')
        node_radius = st.number_input('Radio del nodo', value=0.1, step=0.1)
        submit_button = st.form_submit_button(label='Agregar nodo')

            # Agrega la arista cuando se presiona el botón
        if submit_button:
            # Guarda el estado actual antes de hacer cambios
            st.session_state["previous_nodes"] = copy.deepcopy(st.session_state["nodes"])
            st.session_state["previous_edges"] = copy.deepcopy(st.session_state["edges"])

            node = Node(id=node_id, label=node_label, size=node_radius)
            st.session_state["nodes"].append(node)
elif option == 'Editar':
    with st.sidebar.form(key='edit_node_form'):
        node_id = st.number_input('ID del nodo a editar', value=1, step=1)
        new_node_label = st.text_input('Nueva etiqueta del nodo')
        new_node_radius = st.number_input('Nuevo radio del nodo', value=0.1, step=0.1)
        submit_button = st.form_submit_button(label='Editar nodo')

    if submit_button:
        # Guarda el estado actual antes de hacer cambios
        st.session_state["previous_nodes"] = copy.deepcopy(st.session_state["nodes"])
        st.session_state["previous_edges"] = copy.deepcopy(st.session_state["edges"])

        for node in st.session_state["nodes"]:
            if node.id == node_id:
                node.label = new_node_label
                node.size = new_node_radius

elif option == 'Eliminar':
    with st.sidebar.form(key='delete_node_form'):
        node_id = st.number_input('ID del nodo a eliminar', value=1, step=1)
        submit_button = st.form_submit_button(label='Eliminar nodo')

    # Elimina el nodo cuando se presiona el botón
    if submit_button:
        # Guarda el estado actual antes de hacer cambios
        st.session_state["previous_nodes"] = copy.deepcopy(st.session_state["nodes"])
        st.session_state["previous_edges"] = copy.deepcopy(st.session_state["edges"])

        st.session_state["nodes"] = [node for node in st.session_state["nodes"] if node.id != node_id]
        st.session_state["edges"] = [edge for edge in st.session_state["edges"] if edge.source != node_id and edge.to != node_id]

operation = st.sidebar.selectbox('Arista', ['Agregar', 'Eliminar'])

with st.sidebar:
    with st.form(key='edge_form'):
        if operation == 'Agregar':
            source_id = st.number_input('ID del nodo de origen', value=1, step=1)
            target_id = st.number_input('ID del nodo de destino', value=2, step=1)
            edge_label = st.text_input('Etiqueta de la arista')
            submit_button = st.form_submit_button(label='Ejecutar')

            if submit_button:
            # Guarda el estado actual antes de hacer cambios
                st.session_state["previous_nodes"] = copy.deepcopy(st.session_state["nodes"])
                st.session_state["previous_edges"] = copy.deepcopy(st.session_state["edges"])

                edge = Edge(source=source_id, target=target_id, label=edge_label)
                st.session_state["edges"].append(edge)

  


        elif operation == 'Eliminar':
            source_id_to_remove = st.number_input('ID del nodo de origen', min_value=0, step=1)
            target_id_to_remove = st.number_input('ID del nodo de destino', min_value=0, step=1)
            edge_label_to_remove = st.text_input('Etiqueta de la arista')
            submit_remove_button = st.form_submit_button(label='Eliminar arista')

            # Elimina la arista cuando se presiona el botón
            if submit_remove_button:
                # Guarda el estado actual antes de hacer cambios
                st.session_state["previous_nodes"] = copy.deepcopy(st.session_state["nodes"])
                st.session_state["previous_edges"] = copy.deepcopy(st.session_state["edges"])

                edges_to_remove = []
                for edge in st.session_state["edges"]:
                    if edge.source == source_id_to_remove and edge.to == target_id_to_remove and edge.label == edge_label_to_remove:
                        edges_to_remove.append(edge)
        
                st.session_state["edges"] = [edge for edge in st.session_state["edges"] if edge not in edges_to_remove]
               

# Agrega un botón para deshacer el último cambio
if st.sidebar.button('Deshacer acción anterior'):
    st.session_state["nodes"] = st.session_state["previous_nodes"]
    st.session_state["edges"] = st.session_state["previous_edges"]

# Agrega un botón para guardar el grafo en formato JSON
if st.sidebar.button('Guardar'):
    graph_data = {
        "graph": [
            {
                "data": [
                    {
                        "id": node.id,
                        "label": node.label,
                        "radius": node.size,
                        "linkedTo": [
                            {
                                "nodeId": edge.to,
                                "weight": edge.label
                            } for edge in st.session_state["edges"] if edge.source == node.id
                        ]
                    } for node in st.session_state["nodes"]
                ]
            }
        ]
    }
    st.text(json.dumps(graph_data, indent=4))

# Agrega un botón para mostrar u ocultar el JSON
if st.sidebar.button('Mostrar/Ocultar JSON'):
    st.session_state["show_json"] = not st.session_state["show_json"]

# Muestra el JSON si el usuario ha seleccionado mostrarlo
if st.session_state["show_json"]:
    st.text(st.session_state["json_data"])

# Agrega un botón para deshacer el último cambio
if st.sidebar.button('Deshacer acción anterior'):
    st.session_state["nodes"] = st.session_state["previous_nodes"]
    st.session_state["edges"] = st.session_state["previous_edges"]

# Agrega un botón para guardar el grafo en formato JSON
if st.sidebar.button('Guardar'):
    graph_data = {
        "graph": [
            {
                "data": [
                    {
                        "id": node.id,
                        "label": node.label,
                        "radius": node.size,
                        "linkedTo": [
                            {
                                "nodeId": edge.to,
                                "weight": edge.label
                            } for edge in st.session_state["edges"] if edge.source == node.id
                        ]
                    } for node in st.session_state["nodes"]
                ]
            }
        ]
    }
    st.text(json.dumps(graph_data, indent=4))

# Agrega un botón para mostrar u ocultar el JSON
if st.sidebar.button('Mostrar/Ocultar JSON'):
    st.session_state["show_json"] = not st.session_state["show_json"]

# Muestra el JSON si el usuario ha seleccionado mostrarlo
if st.session_state["show_json"]:
    st.text(st.session_state["json_data"])

# Agrega un menú desplegable en la barra lateral para seleccionar la vista
view_option = st.sidebar.selectbox('Ventana', ['Grafo', 'Matriz'])

if view_option == 'Grafo':
    # Configuración del grafo
    config = Config(width=1000, height=600, directed=True)

    # Visualiza el grafo
    agraph(st.session_state["nodes"], st.session_state["edges"], config)
elif view_option == 'Matriz':
    # Crea una matriz de adyacencia
    node_ids = [node.id for node in st.session_state["nodes"]]
    adjacency_matrix = pd.DataFrame(np.zeros((len(node_ids), len(node_ids))), index=node_ids, columns=node_ids)

    for edge in st.session_state["edges"]:
        adjacency_matrix.loc[edge.source, edge.to] = 1

    # Muestra la matriz de adyacencia
    st.write(adjacency_matrix)