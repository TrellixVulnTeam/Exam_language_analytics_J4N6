# System tools
import os
import sys
sys.path.append(os.path.join(".."))
import numpy as np
import pandas as pd

from collections import Counter
from itertools import combinations 
from tqdm import tqdm

import spacy
nlp = spacy.load("en_core_web_sm")
import argparse

import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20,20)

import networkx as nx


#creating the main function.
def main():
    
    
    '''
    ---------------------Defining commandline arguments:-----------------------
    '''
    #
    ap = argparse.ArgumentParser(description = "[INFO] creating network analysis")
    #first argument: the path to the csv file that one which to create a network analysis from:
    ap.add_argument("-f", #The flag, used before typing this argument.
                    "--file", #The name of the argument
                    required=False, #It is not required to put in a filepath
                    default = "fake_or_real_news.csv", #If no filepathe is put in, the script will use the default filepath.
                    type=str, #This argument must be a string.
                    help="path to file")
    
    ap.add_argument("-e", #The flag, used before typing this argument.
                    "--edges", #The name of the argument
                    required=False, #It is not required to type this argument.
                    default= 10, #If no argument is typed, the number of edges a node must have is set to 10.
                    type=int, #This argument must be a integer 
                    help="The number of edges a node must have to be in the network.")
    
    '''
    Instructing python and the argparse library to parse the arguments.
    Calling vars on the ap.parse_args() to turn it into a python dictionary,
    with the name of the argument as the key and the value is supplied by the user.
    '''
    args = vars(ap.parse_args())
    #Printing the args so the user can se them, when she/he runs it from the terminal.
    print(args)
    
    
    filepath = os.path.join("..", "data", str(args["file"]))
    number_of_edges = args["edges"]
    
    '''
    --------------------Defining filepath:----------------------------
    '''
    
    #First argparse
    #input_file = filepath
    data = pd.read_csv(filepath)
    
    #selecting only data which has the label "REAL"
    real_df = data[data["label"]=="REAL"]["text"]
    
    
    post_entities = []

    #tqdm creates a bar, so the user can se how much of the for-loop has been run through.
    for text in tqdm(real_df):
        # creating temporary list 
        tmp_entities = []
        # create doc object
        doc = nlp(text)
        # for every named entity
        for entity in doc.ents:
            # if that entity is a person
            if entity.label_ == "PERSON":
                # append to temp list
                tmp_entities.append(entity.text)
        # append temp list to main list
        #set makes sure there is no dublicates of names in every tmp_entities.
        post_entities.append(set(sorted(tmp_entities)))
    
    
    '''
    ------------------Creating edgelist:---------------------------------
    '''
    edgelist = []
    # iterate over every document
    for text in post_entities:
        # use itertools.combinations() to create edgelist
        edges = list(combinations(text, 2))
        # for each combination - i.e. each pair of 'nodes'
        for edge in edges:
            # append this to final edgelist
            edgelist.append(tuple(sorted(edge)))
    
    #weighted edgelist
    counted_edges = []
    for key, value in Counter(edgelist).items():
        source = key[0]
        target = key[1]
        weight = value
        counted_edges.append((source, target, weight))
    
    
    edges_df = pd.DataFrame(counted_edges, columns=["nodeA", "nodeB", "weight"])
    print(edges_df.head(10))
    
    
    '''
    ----------------------Filtereing based on edgeweight:------------------------
    '''
    
    #The nodes must have a weight higher than the number of edges givin from the user.
    filtered = edges_df[edges_df["weight"]>number_of_edges] #number_of_edges = CLI argument, edges.
    #Defining Graph: G
    G=nx.from_pandas_edgelist(filtered, 'nodeA', 'nodeB', ["weight"])
    
    
    #Drawing graph.
    nx.draw_random(G, with_labels=True, node_size=50, font_size=10)
    
    #Saving the path of the output for the vizualisation.
    outpath_viz = os.path.join("..", "viz", "network.png")
    #Saving graph.
    plt.savefig(outpath_viz, dpi=300, bbox_inches='tight')
    #plt.show()
    
    
    '''
    ----------Creating a dataframe that contains degree centrality, eigenvector and betweennes:----------------
    '''
    # Calculating the number of ties the nodes have.
    dg = nx.degree_centrality(G)
    # Calculating the influence of the different nodes in the network.
    ev = nx.eigenvector_centrality(G)
    # Calculating the mesure of the shortest path from a node to a node for each node.
    bc = nx.betweenness_centrality(G)
    
    #Sorting values
    dg_df = pd.DataFrame(dg.items()).sort_values(weight, ascending=False)
    ev_df = pd.DataFrame(ev.items()).sort_values(weight, ascending=False)
    bc_df = pd.DataFrame(bc.items()).sort_values(weight, ascending=False)
    
    # Renaming column names:
    dg_df.columns = ["Name", "degree_centrality"]
    
    bc_df.columns = ["Name", "betweenness_centrality"]

    ev_df.columns = ["Name", "eigenvector_centrality"]

    #Merging dataframes:
    final_df = pd.merge(bc_df, ev_df, on='Name')
    
    final_df = pd.merge(dg_df, final_df, on='Name')
    
    final_df.to_csv(os.path.join("..", "output", "final_df.csv"))

    print(final_df.head(10))
    
if __name__ =='__main__':
    main()