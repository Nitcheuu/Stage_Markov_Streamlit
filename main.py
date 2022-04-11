import streamlit as st
import numpy as np
import random as r
import pandas as pd
import graphviz as g
from Probas.probas import algo_etude_probas
from Stats.stats import algo_etude_stats
import os
import pydot

os.environ["PATH"] += "./bin"

couleurs : list[str] = ["#f00000", "#00f000", "#0000f0", "black", "turquoise", "sienna", "grey", "red", "green", "blue", "black", "turquoise", "sienna", "grey"]

# Liste qui contient le nom de tous les datasets
liste_dataset : list[str] = os.listdir("./datasets")

# Définition du titre de la sidebar
st.sidebar.title("Paramètres")

# Nombre de période T de temps
k = st.sidebar.slider(label="Nombre d'instants t : ", min_value=1, max_value=100)

# Liste déroulante du choix du dataset
dataset = st.sidebar.selectbox("Importer un dataset : ", liste_dataset)

# Lecture du dataset
Q_df = pd.read_excel(f"C:/Users/Favrelle/PycharmProjects/chaineMarkov/datasets/{dataset}")
Q_df = pd.DataFrame(Q_df).transpose()

# Définition de la matrice de transition à partir du dataframe
Q = np.array(Q_df)

# Définition de l'ensemble E
E = []
for index in Q_df.index:
    E.append(index)

# Taille de l'ensemble E
taille_E = len(E)

# Liste qui contiendra la loi de X pour k=0
st.sidebar.text("Vecteur P : ")

# Définition du vecteur P
P = []
for i in range(taille_E):
    P.append(st.sidebar.slider(f"P(X = {E[i]}) pour k = 0 : ", min_value=0., max_value=1., step=0.01, key=f"X[{i}]"))
P = np.array(P, dtype=np.float64) # On convertit en np array pour plus de rapidité

# Mise en forme des données pour le vecteur P
P_df = pd.DataFrame(P)
P_df = P_df.transpose()
for i in range(taille_E):
    P_df = P_df.rename(columns={i: f"i={E[i]}"})
P_df = P_df.rename(index={0: "P(X=i) pour k=0"})

# Partie stats #
st.sidebar.write("Partie statistiques")
st.sidebar.text("Définir la répartition des sujets pour k=0")

# Répartition des sujets
P_stats = []
for i in range(taille_E):
    P_stats.append(st.sidebar.slider(f"Pour l'objet {E[i]}", min_value=0, max_value=1000))

# Simulation statistique
stats = algo_etude_stats(Q, np.array(P_stats), k)
valid_button = st.sidebar.button("Faire l'étude avec ces paramètres")

# Définition du graphe
graph = g.Digraph(format="png")
# Ajout des sommets qui correspondent à l'ensemble E
for i in range(len(E)):
    graph.node(E[i], E[i], color=couleurs[i], fillcolor=couleurs[i], style="filled", fontcolor="white")
# Ajout des arcs
for y in range(taille_E):
    for i in range(taille_E):
        # On ne réprésente pas les chemins impossibles
        if Q[y][i] != 0.0:
            # On met une couleur plus fable pour
            if Q[y][i] < 0.1:
                graph.edge(E[y], E[i], label=f"{Q[y][i]}", color="orange")
            else:
                graph.edge(E[y], E[i], label=f"{Q[y][i]}", color="red")

graph.save("test.dot")
(graphe,) = pydot.graph_from_dot_file("./test.dot")
print("ok")
graphe.write_png("output.png")
help(pydot.Dot.write)


######## AFFICHAGE ########
print(graph.source)
st.title("Etude des probabilités")

st.text("Matrice de transition : ")
st.write(Q_df)
try:
    st.text(f"On lit : P({E[taille_E - 1]}|{E[0]}) = {P[taille_E - 1][0]}")
except:
    pass

st.write("Vecteur P : ")
st.write(P_df)

st.write("Chaine de Markov : ")
st.graphviz_chart(graph)

P, X_data = algo_etude_probas(Q, P, k, taille_E)

st.write("Valeur de P(X) en fonction de k : ")
st.line_chart(pd.DataFrame(X_data.T, columns=E))
try:
    st.text(f"On lit : quand k = {k//2}, P(X={E[0]}) = {X_data[0][k // 2]}")
except:
    pass

P = np.array(P, dtype=np.float64).reshape((taille_E, 1), order='F')
P_df = pd.DataFrame(P)
for i in range(taille_E):
    P_df = P_df.rename(index={i: f"i={E[i]}"})
P_df = P_df.rename(columns={0: f"P(X=i) pour k={k}"})

st.write(f"Loi de X pour k = {k} : ")
st.write(P_df)

st.title("Etude statistiques")
st.write(f"Pour {np.sum(P_stats)} sujet(s)")
st.line_chart(pd.DataFrame(stats, columns=E))

try:
    st.write(f"On lit : quand k = {k//2}, il y a {stats.T[0][k//2] * 100}% de sujet(s) dans {E[0]}")
except:
    pass


stats = pd.DataFrame(stats, columns=E)
st.write(stats)

st.button("Refaire une étude statistiques")



