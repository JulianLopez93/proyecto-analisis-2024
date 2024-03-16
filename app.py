import streamlit as st
from streamlit_agraph import Node, Edge, Config, agraph
import json

# Agrega un selector de archivos en la barra lateral
uploaded_file = st.sidebar.file_uploader("Elige un archivo JSON", type="json")

# Crea listas para los nodos y las aristas
nodes = []
edges = []

if uploaded_file is not None:
    # Lee el archivo JSON
    data = json.load(uploaded_file)

    # Añade nodos y aristas a las listas
    for item in data['graph'][0]['data']:
        node = Node(id=item['id'], label=item['label'], size=item['radius'])
        nodes.append(node)
        for linked_node in item['linkedTo']:
            edge = Edge(source=item['id'], target=linked_node['nodeId'], label=str(linked_node['weight']))
            edges.append(edge)


operation = st.sidebar.selectbox('Arista', ['Agregar', 'Editar', 'Eliminar'])

with st.sidebar:
    with st.form(key='edge_form'):
        if operation == 'Agregar':
            source_id = st.number_input('ID del nodo de origen', value=1, step=1)
            target_id = st.number_input('ID del nodo de destino', value=2, step=1)
            edge_label = st.text_input('Etiqueta de la arista')
            submit_button = st.form_submit_button(label='Ejecutar')

            # Agrega la arista cuando se presiona el botón
            if submit_button:
                edge = Edge(source=source_id, target=target_id, label=edge_label)
                edges.append(edge)

        elif operation == 'Editar':
            source_id_to_edit = st.number_input('ID del nodo de origen', min_value=0, step=1)
            target_id_to_edit = st.number_input('ID del nodo de destino', min_value=0, step=1)
            edge_label = st.text_input('Etiqueta de la arista')
            edge_to_edit = None

            for edge in edges:
                if (edge.source, edge.to) == (source_id_to_edit, target_id_to_edit):
                    edge_to_edit = edge
                    break

            if edge_to_edit:
                edge_label_edit = st.text_input('Nueva etiqueta de la arista', value=edge_to_edit.label)
                submit_edit_button = st.form_submit_button(label='Editar arista')

                # Edita la arista cuando se presiona el botón
                if submit_edit_button:
                    edge_to_edit.label = edge_label_edit
            else:
                st.warning('La arista no existe. Introduce IDs válidos para editar.')

        elif operation == 'Eliminar':
            source_id_to_remove = st.number_input('ID del nodo de origen', min_value=0, step=1)
            target_id_to_remove = st.number_input('ID del nodo de destino', min_value=0, step=1)
            edge_label_to_remove = st.text_input('Etiqueta de la arista')
            submit_remove_button = st.form_submit_button(label='Eliminar arista')

            # Elimina la arista cuando se presiona el botón
            if submit_remove_button:
                edges_to_remove = []
                for edge in edges:
                    if edge.source == source_id_to_remove and edge.to == target_id_to_remove and edge.label == edge_label_to_remove:
                        edges_to_remove.append(edge)
        
                edges = [edge for edge in edges if edge not in edges_to_remove]

# Configuración del grafo
config = Config(width=500, height=500, directed=True)

# Visualiza el grafo
agraph(nodes, edges, config)

