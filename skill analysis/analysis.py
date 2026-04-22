# =============================================
# Skill Monopoly & Dependency Analysis (Clear Tables + Visuals)
# =============================================

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

print("Starting Skill Monopoly & Dependency Analysis...")

# -------------------------------
# STEP 1: Load Datasets
# -------------------------------
skill_count = pd.read_csv(
    r"D:\Data visualization ass 1\skill_count.tsv",
    sep='\t', header=None, usecols=[0,1]
)
skill_count.columns = ['skill','count']
skill_count['skill'] = skill_count['skill'].str.strip()
print(f"skill_count loaded with {skill_count.shape[0]} skills")
print(skill_count.head(5))

skill_pairs = pd.read_csv(
    r"D:\Data visualization ass 1\skill_pair_count.tsv",
    sep='\t', header=None, usecols=[0,1,2]
)
skill_pairs.columns = ['skill1','skill2','co_occurrence_count']
skill_pairs['skill1'] = skill_pairs['skill1'].str.strip()
skill_pairs['skill2'] = skill_pairs['skill2'].str.strip()
print(f"skill_pairs loaded with {skill_pairs.shape[0]} pairs")
print(skill_pairs.head(5))

# -------------------------------
# STEP 2: Compute Jaccard for pairs
# -------------------------------
skill_totals = dict(zip(skill_count['skill'], skill_count['count']))

def jaccard(s1, s2, cooc):
    total1 = skill_totals.get(s1,0)
    total2 = skill_totals.get(s2,0)
    denom = total1 + total2 - cooc
    return cooc/denom if denom>0 else 0

skill_pairs['jaccard'] = skill_pairs.apply(
    lambda row: jaccard(row['skill1'], row['skill2'], row['co_occurrence_count']),
    axis=1
)

print("Jaccard similarity computed!")

# -------------------------------
# STEP 3: Build Network (filtered)
# -------------------------------
G = nx.Graph()
threshold = 0.05

for _, row in skill_pairs.iterrows():
    if row['jaccard'] > threshold:
        G.add_edge(row['skill1'], row['skill2'], weight=row['jaccard'])

print(f"Network built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# -------------------------------
# STEP 4: Centrality Measures
# -------------------------------
deg_cent = nx.degree_centrality(G)
bet_cent = nx.betweenness_centrality(G, weight='weight', k=500)

top_gateway = sorted(deg_cent.items(), key=lambda x:x[1], reverse=True)[:10]
top_monopoly = sorted(bet_cent.items(), key=lambda x:x[1], reverse=True)[:10]

gateway_df = pd.DataFrame(top_gateway, columns=['Skill','Gateway_Score'])
monopoly_df = pd.DataFrame(top_monopoly, columns=['Skill','Monopoly_Score'])

# -------------------------------
# STEP 5: Print Tables
# -------------------------------
print("\n📊 Top 10 Gateway Skills (Degree Centrality):")
print(gateway_df.to_string(index=False))

print("\n📊 Top 10 Skill Monopolies (Betweenness Centrality):")
print(monopoly_df.to_string(index=False))

# -------------------------------
# STEP 6: Visualizations
# -------------------------------

# 1️⃣ Gateway Skills Bar Chart
plt.figure(figsize=(10,6))
plt.barh(gateway_df['Skill'][::-1], gateway_df['Gateway_Score'][::-1], color='navy')
plt.xlabel("Gateway Score")
plt.title("Top 10 Gateway Skills")
plt.tight_layout()
plt.savefig(r"D:\Data visualization ass 1\gateway_bar_chart.png", dpi=300)
plt.close()

# 2️⃣ Monopoly Skills Bar Chart
plt.figure(figsize=(10,6))
plt.barh(monopoly_df['Skill'][::-1], monopoly_df['Monopoly_Score'][::-1], color='steelblue')
plt.xlabel("Monopoly Score")
plt.title("Top 10 Skill Monopolies")
plt.tight_layout()
plt.savefig(r"D:\Data visualization ass 1\monopoly_bar_chart.png", dpi=300)
plt.close()

# 3️⃣ Simplified Network Plot (top 50 skills + neighbors)
top_nodes = [skill for skill,_ in top_gateway[:50]]
subgraph = G.subgraph(top_nodes + [n for skill in top_nodes for n in G.neighbors(skill)])
plt.figure(figsize=(12,10))
pos = nx.spring_layout(subgraph, seed=42)
node_colors = ['orange' if node in gateway_df['Skill'].values else 'skyblue' for node in subgraph.nodes()]
nx.draw(subgraph, pos, with_labels=True, node_color=node_colors, node_size=400, font_size=8)
plt.title("Simplified Skill Network (Top Gateway Skills Highlighted)")
plt.tight_layout()
plt.savefig(r"D:\Data visualization ass 1\network_plot.png", dpi=300)
plt.close()

# 4️⃣ Dependency Chain Subgraph
top_skill = gateway_df.iloc[0]['Skill']
neighbors = list(G.neighbors(top_skill))[:20]
subgraph_dep = G.subgraph([top_skill] + neighbors)
plt.figure(figsize=(8,6))
pos = nx.spring_layout(subgraph_dep, seed=42)
nx.draw(subgraph_dep, pos, with_labels=True, node_color="lightgreen", node_size=600, font_size=9)
plt.title(f"Dependency Chain for {top_skill}")
plt.tight_layout()
plt.savefig(r"D:\Data visualization ass 1\dependency_chain.png", dpi=300)
plt.close()

# -------------------------------
# STEP 7: Export Results
# -------------------------------
gateway_df.to_csv(r"D:\Data visualization ass 1\top_gateway_skills.csv", index=False)
monopoly_df.to_csv(r"D:\Data visualization ass 1\top_skill_monopolies.csv", index=False)

print("\n✅ Analysis complete! Tables printed and visuals saved:")
print(" - gateway_bar_chart.png")
print(" - monopoly_bar_chart.png")
print(" - network_plot.png")
print(" - dependency_chain.png")
