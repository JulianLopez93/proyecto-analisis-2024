import streamlit as st
from streamlit_agraph import Node, Edge, Config, agraph
import json
import pandas as pd
import numpy as np
import copy
import io
import base64
import networkx as nx
import matplotlib.pyplot as plt
import tempfile
import random

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
if "json_data" not in st.session_state: 
    st.session_state["json_data"] = "" 


expander=st.sidebar.expander("Archivo")
with expander:
# Agrega un selector de archivos en la barra lateral
    uploaded_file = st.file_uploader("Elige un archivo JSON", type="json")

    if uploaded_file is not None and not st.session_state["nodes"] and not st.session_state["edges"]:
        # Lee el archivo JSON
        data = json.load(uploaded_file)

        # Añade nodos y aristas a las listas
        for item in data['graph'][0]['data']:
            node = Node(id=item['id'], label=item['label'], size=item['radius'])
            st.session_state["nodes"].append(node)
            for linked_node in item['linkedTo']:
                edge = Edge(source=item['id'], target=linked_node['nodeId'], label=str(linked_node['weight']), color=linked_node.get('color', 'black'), linestyle=linked_node.get('linestyle', 'solid'))
                st.session_state["edges"].append(edge)



    # Agrega un botón para guardar el grafo en formato JSON

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
                                "weight": edge.label,
                                "color": edge.color
                            } for edge in st.session_state["edges"] if edge.source == node.id
                        ]
                    } for node in st.session_state["nodes"]
                ]
            }
        ]
    }
    json_data = json.dumps(graph_data, indent=4)
    st.session_state["json_data"] = base64.b64encode(json_data.encode())

    # Convertimos el grafo a un DataFrame de pandas
    df = pd.json_normalize(graph_data['graph'], record_path=['data'])

    # Creamos un grafo vacío
    G = nx.Graph()

    # Añadimos los nodos al grafo
    for node in graph_data['graph'][0]['data']:
        G.add_node(node['id'], label=node['label'])

    # Añadimos las aristas al grafo
    for node in graph_data['graph'][0]['data']:
        for edge in node['linkedTo']:
            G.add_edge(node['id'], edge['nodeId'], weight=edge['weight'])

    # Creamos un objeto BytesIO
    output = io.BytesIO()
    # Escribimos el DataFrame en el objeto BytesIO como un archivo de Excel
    df.to_excel(output, index=False)
    # Movemos el cursor al inicio del objeto BytesIO
    output.seek(0)

    # Dibujamos el grafo
    plt.figure()
    nx.draw(G, with_labels=True)

    # Creamos un archivo temporal para guardar la imagen
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        plt.savefig(tmpfile.name)
        tmpfile.flush()

    # Agrega un botón para descargar el grafo en formato JSON
    st.download_button(
        label="Descargar JSON",
        data=base64.b64decode(st.session_state["json_data"]).decode(),
        file_name='graph.json',
        mime='application/json'
    )

    # Creamos el botón de descarga en la barra lateral
    st.download_button(
        label="Exportar como Excel",
        data=output,
        file_name='grafo_editado.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Creamos el botón de descarga en la barra lateral
    st.download_button(
        label="Exportar como imagen",
        data=open(tmpfile.name, "rb").read(),
        file_name='grafo.png',
        mime='image/png'
    )


# Agrega un título en la barra lateral
st.sidebar.markdown("## Editar")

# Agrega un botón para deshacer la última acción
if st.sidebar.button('Deshacer acción anterior'):
    st.session_state["nodes"] = st.session_state["previous_nodes"]
    st.session_state["edges"] = st.session_state["previous_edges"]



# Agrega un menú desplegable en la barra lateral para seleccionar el tipo de grafo
option = st.sidebar.selectbox('Nuevo grafo', ['Personalizado', 'Aleatorio'])

if option == 'Personalizado':
    # Agrega un menú desplegable en la barra lateral
    option2 = st.sidebar.selectbox('Nodo', ['Agregar', 'Editar', 'Eliminar'])

        # Agrega, edita o elimina un nodo dependiendo de la opción seleccionada
    if option2 == 'Agregar':
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
    elif option2 == 'Editar':
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

    elif option2 == 'Eliminar':
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

    operation = st.sidebar.selectbox('Arista', ['Agregar', 'Eliminar','Editar'])

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
                    edges_to_remove = []
                    for edge in st.session_state["edges"]:
                        if ((edge.source == source_id_to_remove and edge.to == target_id_to_remove) or 
                            (edge.source == target_id_to_remove and edge.to == source_id_to_remove)) and edge.label == edge_label_to_remove:
                            edges_to_remove.append(edge)
            
                    st.session_state["edges"] = [edge for edge in st.session_state["edges"] if edge not in edges_to_remove]
            elif operation == 'Editar':
                source_id_to_edit = st.number_input('ID del nodo de origen', min_value=0, step=1)
                target_id_to_edit = st.number_input('ID del nodo de destino', min_value=0, step=1)
                edge_label_to_edit = st.text_input('Etiqueta de la arista actual')
                new_edge_label = st.text_input('Nueva etiqueta de la arista')
                new_edge_color = st.color_picker('Nuevo color de la arista')
                new_edge_linestyle = st.selectbox('Nuevo estilo de línea', ['solid', 'dashed', 'dotted', 'dashdot'])
                submit_edit_button = st.form_submit_button(label='Editar arista')

                # Edita la arista cuando se presiona el botón
                if submit_edit_button:
                    for edge in st.session_state["edges"]:
                        if ((edge.source == source_id_to_edit and edge.to == target_id_to_edit) or (edge.source == target_id_to_edit and edge.to == source_id_to_edit)) and edge.label == edge_label_to_edit:
                            edge.label = new_edge_label
                            edge.color = new_edge_color
                            edge.linestyle = new_edge_linestyle
elif option == 'Aleatorio':
    with st.sidebar.form(key='random_graph_form'):
        num_nodes = st.number_input('Cantidad de nodos', value=5, step=1)
        complete_graph = st.checkbox('Grafo completo')
        connected_graph = st.checkbox('Grafo conexo')
        weighted_graph = st.checkbox('Grafo ponderado')
        directed_graph = st.checkbox('Grafo dirigido')
        submit_button = st.form_submit_button(label='Crear grafo aleatorio')

        if submit_button:
            # Guarda el estado actual antes de hacer cambios
            st.session_state["previous_nodes"] = copy.deepcopy(st.session_state["nodes"])
            st.session_state["previous_edges"] = copy.deepcopy(st.session_state["edges"])

            # Limpia los nodos y aristas actuales
            st.session_state["nodes"] = []
            st.session_state["edges"] = []

            # Crea los nodos
            for i in range(num_nodes):
                node = Node(id=i+1, label=f'N{i+1}', size=random.uniform(0.1, 1))
                st.session_state["nodes"].append(node)

            # Crea las aristas
            for i in range(num_nodes):
                for j in range(i+1, num_nodes):
                    if complete_graph or (connected_graph and j == i+1) or random.random() < 0.5:
                        weight = random.randint(1, 100) if weighted_graph else None
                        edge = Edge(source=i+1, target=j+1, label=weight)
                        st.session_state["edges"].append(edge)
                        if not directed_graph and i != j:
                            edge = Edge(source=j+1, target=i+1, label=weight)
                            st.session_state["edges"].append(edge)




# Agrega un botón en la barra lateral para determinar si el grafo es bipartito
if st.sidebar.button('Determinar si es bipartito'):
    is_bipartite = nx.is_bipartite(G)
    if is_bipartite:
        st.sidebar.write('El grafo es bipartito.')
    else:
        st.sidebar.write('El grafo no es bipartito.')

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