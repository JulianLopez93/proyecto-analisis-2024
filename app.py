import streamlit as st
from streamlit_agraph import Node, Edge, Config, agraph
import json

# Inicializa st.session_state si aún no se ha hecho
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "edges" not in st.session_state:
    st.session_state["edges"] = []

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

    if submit_button:
        node = Node(id=node_id, label=node_label, size=node_radius)
        st.session_state["nodes"].append(node)

elif option == 'Editar':
    with st.sidebar.form(key='edit_node_form'):
        node_id = st.number_input('ID del nodo a editar', value=1, step=1)
        new_node_label = st.text_input('Nueva etiqueta del nodo')
        new_node_radius = st.number_input('Nuevo radio del nodo', value=0.1, step=0.1)
        submit_button = st.form_submit_button(label='Editar nodo')

    if submit_button:
        for node in st.session_state["nodes"]:
            if node.id == node_id:
                node.label = new_node_label
                node.size = new_node_radius

elif option == 'Eliminar':
    with st.sidebar.form(key='delete_node_form'):
        node_id = st.number_input('ID del nodo a eliminar', value=1, step=1)
        submit_button = st.form_submit_button(label='Eliminar nodo')

    if submit_button:
        st.session_state["nodes"] = [node for node in st.session_state["nodes"] if node.id != node_id]
        st.session_state["edges"] = [edge for edge in st.session_state["edges"] if edge.source != node_id and edge.target != node_id]

# Configuración del grafo
config = Config(width=500, height=500, directed=True)

# Visualiza el grafo
agraph(st.session_state["nodes"], st.session_state["edges"], config)