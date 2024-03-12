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

# Agrega un formulario en la barra lateral
with st.sidebar.form(key='add_node_form'):
    node_id = st.number_input('ID del nodo', value=1, step=1)
    node_label = st.text_input('Etiqueta del nodo')
    node_radius = st.number_input('Radio del nodo', value=0.1, step=0.1)
    submit_button = st.form_submit_button(label='Agregar nodo')

# Agrega el nodo cuando se presiona el botón
if submit_button:
    node = Node(id=node_id, label=node_label, size=node_radius)
    nodes.append(node)

# Configuración del grafo
config = Config(width=500, height=500, directed=True)

# Visualiza el grafo
agraph(nodes, edges, config)