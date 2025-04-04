import pydot
from bson.objectid import ObjectId
import random
import traceback

def detect_relationships(db_data):
    detected_relationships = set()
    collection_names = list(db_data.keys())
    print("\n--- Iniciando detección automática de relaciones ---")
    for source_collection_name, collection_data in db_data.items():
        if not collection_data:
            print(f"Colección '{source_collection_name}' está vacía, saltando...")
            continue
        first_doc = collection_data[0]
        print(f"Analizando campos del primer documento en '{source_collection_name}': {list(first_doc.keys())}")
        for field_name, field_value in first_doc.items():
            if field_name.endswith("_id") and field_name != "_id" and isinstance(field_value, ObjectId):
                print(f"  > Campo encontrado '{field_name}' en '{source_collection_name}' que parece una clave foránea.")
                base_name = field_name[:-3]
                potential_target_names = [base_name, base_name + 's']
                target_collection_name_found = None
                for potential_target in potential_target_names:
                    if potential_target in collection_names:
                        if potential_target != source_collection_name:
                             target_collection_name_found = potential_target
                             print(f"    >> Posible referencia a la colección: '{target_collection_name_found}'")
                             break
                if target_collection_name_found:
                    relation_tuple = (target_collection_name_found, source_collection_name, "1:N", field_name)
                    if relation_tuple not in detected_relationships:
                        print(f"    ✅ Relación detectada: {relation_tuple[0]} --({relation_tuple[3]})--> {relation_tuple[1]} ({relation_tuple[2]})")
                        detected_relationships.add(relation_tuple)
                    else:
                         print(f"    -> Relación {relation_tuple} ya detectada previamente.")
                else:
                    print(f"    ⚠️ No se encontró una colección correspondiente para '{field_name}' (se buscaron: {potential_target_names})")
    print("--- Detección de relaciones finalizada ---")
    return list(detected_relationships)

x = random.randint(1, 1000)
def generate_erd_graphviz_with_data_types(db_data, output_filename="Graph " + str(x) + " .png"):
    try:
        graph = pydot.Dot(graph_type='digraph', rankdir='LR')
        colors = ["lightblue", "lightgreen", "lightyellow", "lightcoral", "lightcyan", "lightsalmon", "lightpink", "lightgrey"]
        print("\n--- Creando nodos para las colecciones ---")
        color_index = 0
        for collection_name, collection_data in db_data.items():
            node_color = colors[color_index % len(colors)]
            color_index += 1
            node_label = f"{collection_name}\n{'-'*len(collection_name)}\n"
            if collection_data:
                first_doc = collection_data[0]
                attribute_types = []
                for attr, value in first_doc.items():
                    data_type = type(value).__name__
                    if isinstance(value, ObjectId):
                        data_type = "ObjectId"
                    elif isinstance(value, list):
                         data_type = "list"
                    attribute_types.append(f"{attr}: {data_type}")
                node_label += "\n".join(attribute_types)
                node = pydot.Node(collection_name, label=node_label, shape='box', style="filled", fillcolor=node_color)
                graph.add_node(node)
                print(f"Nodo creado para '{collection_name}' con {len(attribute_types)} atributos.")
            else:
                node_label += "(Colección Vacía)"
                node = pydot.Node(collection_name, label=node_label, shape='box', style="filled", fillcolor=node_color, fontcolor="gray")
                graph.add_node(node)
                print(f"Nodo creado para colección vacía: '{collection_name}'.")
        print("--- Nodos creados ---")
        relationships = detect_relationships(db_data)
        print("\n--- Añadiendo aristas para las relaciones detectadas ---")
        if not relationships:
             print("No se detectaron relaciones automáticamente.")
        else:
            for src, dest, cardinality, attribute in relationships:
                if graph.get_node(src) and graph.get_node(dest):
                    edge = pydot.Edge(src, dest, label=f"{cardinality}\n({attribute})")
                    graph.add_edge(edge)
                    print(f"Arista añadida: {src} -> {dest} [{attribute}]")
                else:
                     print(f"⚠️ Advertencia: Nodo '{src}' o '{dest}' no encontrado en el grafo. No se pudo añadir la arista para ({src}, {dest}, {attribute}).")
        print("--- Aristas añadidas ---")
        print(f"\nIntentando guardar el gráfico en: {output_filename}")
        graph.write_png(output_filename)
        print(f"✅ Diagrama ERD con detección automática de relaciones guardado exitosamente en: {output_filename}")

    except ImportError as ie:
         print(f"\n❌ ERROR DE IMPORTACIÓN: {ie}")
         print("Parece que 'pydot' o su dependencia 'Graphviz' no están instalados o configurados correctamente.")
         print("Para instalar pydot, usa: pip install pydot")
         print("Graphviz también debe estar instalado en tu sistema Y en el PATH.")
         print("Descarga Graphviz desde: https://graphviz.org/download/")
         print("Asegúrate de añadir la carpeta 'bin' de Graphviz a la variable de entorno PATH.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado durante la generación del gráfico: {e}")
        print("\n--- Traceback detallado ---")
        traceback.print_exc()
        print("--------------------------")

user1_id = ObjectId()
user2_id = ObjectId()
user3_id = ObjectId()
post1_id = ObjectId()
post2_id = ObjectId()
post3_id = ObjectId()
comment1_id = ObjectId()
comment2_id = ObjectId()
comment3_id = ObjectId()
category1_id = ObjectId()
category2_id = ObjectId()
tag1_id = ObjectId()
tag2_id = ObjectId()
tag3_id = ObjectId()
product1_id = ObjectId()
product2_id = ObjectId()
review1_id = ObjectId()
review2_id = ObjectId()
review3_id = ObjectId()
tagging1_id = ObjectId()
tagging2_id = ObjectId()
tagging3_id = ObjectId()
tagging4_id = ObjectId()

db_data = {
    "users": [
        {"_id": user1_id, "name": "Alice", "city": "Metropolis"},
        {"_id": user2_id, "name": "Bob", "city": "Gotham"},
        {"_id": user3_id, "name": "Charlie", "city": "Star City"}
    ],
    "categories": [
        {"_id": category1_id, "name": "Tutorials", "type": "blog"},
        {"_id": category2_id, "name": "Electronics", "type": "store"}
    ],
    "posts": [
        {"_id": post1_id, "title": "Advanced Python", "content": "...", "user_id": user1_id, "category_id": category1_id},
        {"_id": post2_id, "title": "Intro to MongoDB", "content": "...", "user_id": user2_id, "category_id": category1_id},
        {"_id": post3_id, "title": "Data Viz", "content": "...", "user_id": user1_id, "category_id": category1_id}
    ],
    "comments": [
        {"_id": comment1_id, "text": "Very helpful!", "post_id": post1_id, "user_id": user2_id},
        {"_id": comment2_id, "text": "Good explanation.", "post_id": post2_id, "user_id": user1_id},
        {"_id": comment3_id, "text": "I have a question...", "post_id": post1_id, "user_id": user3_id}
    ],
    "products": [
        {"_id": product1_id, "name": "Laptop Pro", "price": 1200.00, "seller_id": user1_id, "category_id": category2_id},
        {"_id": product2_id, "name": "Wireless Mouse", "price": 25.50, "seller_id": user2_id, "category_id": category2_id}
    ],
    "reviews": [
        {"_id": review1_id, "text": "Excellent product!", "rating": 5, "product_id": product1_id, "user_id": user2_id},
        {"_id": review2_id, "text": "Works great.", "rating": 4, "product_id": product2_id, "user_id": user3_id},
        {"_id": review3_id, "text": "Good value for money.", "rating": 4, "product_id": product1_id, "user_id": user3_id}
    ],
    "tags": [
        {"_id": tag1_id, "name": "python"},
        {"_id": tag2_id, "name": "database"},
        {"_id": tag3_id, "name": "webdev"}
    ],
    "taggings": [
        {"_id": tagging1_id, "post_id": post1_id, "tag_id": tag1_id},
        {"_id": tagging2_id, "post_id": post2_id, "tag_id": tag2_id},
        {"_id": tagging3_id, "post_id": post1_id, "tag_id": tag3_id},
        {"_id": tagging4_id, "post_id": post3_id, "tag_id": tag1_id}
    ]
}

generate_erd_graphviz_with_data_types(db_data)