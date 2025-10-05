import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container


st.title("ventes aux etats unis")
df = pd.read_csv('ventes.csv')
# filtrer par date
## conversion de la colonne date
df['order_date'] = pd.to_datetime(df['order_date'])

# Définir les bornes possibles
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()
col1, col2 = st.columns(2)
with col1:
    date_debut = st.date_input(
        "Date de début",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

with col2:
    date_fin = st.date_input(
        "Date de fin",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

# Vérification des dates
if date_debut > date_fin:
    st.warning("La date de début ne peut pas être postérieure à la date de fin.")

    # Filtrage
date_debut = pd.to_datetime(date_debut)
date_fin = pd.to_datetime(date_fin)
    
df = df[(df['order_date'] >= date_debut) & (df['order_date'] <= date_fin)]



# Dictionnaire de conversion : abréviation ➜ nom complet
abbr_to_state = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Ajouter la colonne avec les noms complets
df['State_complet'] = df['State'].map(abbr_to_state)

st.sidebar.subheader("Filtrer par :")

# Filtrage par region
region_dispo = df['Region'].unique().tolist()
region = st.sidebar.multiselect("Region", region_dispo)

if region:
    df = df[df['Region'].isin(region)]

#Filtrage par etat
state_dispo = df['State_complet'].unique().tolist()
state = st.sidebar.multiselect("State", state_dispo)
if state:
    df = df[df['State_complet'].isin(state)]

#Filtrage par contry
county_dispo = df['County'].unique().tolist()
county = st.sidebar.multiselect("County", county_dispo)
if county:
    df = df[df['County'].isin(county)]

#Filtrage par city
city_dispo = df['City'].unique().tolist()
City = st.sidebar.multiselect("City", city_dispo)
if City:
    df = df[df['City'].isin(City)]


statuts_disponibles = df['status'].unique().tolist()

# Multiselect dans la sidebar
statut_selection = st.multiselect(
    "Filtrer par statut de commande :",
    options=statuts_disponibles
)

# Filtrage du DataFrame
if statut_selection:
    df = df[df['status'].isin(statut_selection)]


total_ventes = df['total'].sum()
nb_clients = df['cust_id'].nunique()
nb_commandes = df['order_id'].nunique()

# Fonction pour créer une carte
def kpi_card(title, value, emoji):
    st.markdown(f"""
        <div style='
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        '>
            <div style='font-size:16px; color:#555;'>{emoji} {title}</div>
            <div style='font-size:32px; font-weight:bold; color:#1f77b4;'>{value}</div>
        </div>
    """, unsafe_allow_html=True)

# Affichage en colonnes
col1, col2, col3 = st.columns(3)

with col1:
    kpi_card("Total des ventes", f"${total_ventes:,.0f}", "💰")

with col2:
    kpi_card("Nombre de Clients", nb_clients, "👥")

with col3:
    kpi_card("Commandes", nb_commandes, "🧾")

# Regrouper les données
# Comptage des ventes par catégorie et par région
ventes_par_categorie = df['category'].value_counts()
ventes_par_region = df['Region'].value_counts()

# Création de deux colonnes côte à côte dans Streamlit
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ventes par Catégorie")
    fig1 = px.bar(
        x=ventes_par_categorie.index,
        y=ventes_par_categorie.values,
        text=ventes_par_categorie.values,
        labels={'x': "Catégorie", 'y': "Nombre de ventes"},
        color=ventes_par_categorie.index
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig1)

with col2:
    st.subheader("Ventes par Région")
    fig2 = px.pie(
        names=ventes_par_region.index,
        values=ventes_par_region.values,
        hole=0.4,  # tu peux mettre hole=0.3 pour un donut
    )
    st.plotly_chart(fig2)





st.subheader("Top 10 des Meilleurs Clients")
if st.checkbox("par le nombre des commandes"):
    # Regrouper par client et trier par nombre de ventes
    top_clients = df['full_name'].value_counts().sort_values(ascending=False).head(10)

    # Création du barplot
    fig3 = px.bar(
        x=top_clients.values,
        y=top_clients.index,
        orientation='h',
        text=top_clients.values,
        labels={'x': 'Nombre de commandes', 'y': 'Client'},
        color=top_clients.values,
        color_continuous_scale='Tealgrn'
    )
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

if st.checkbox("par le montant generer"):
    # Regrouper la somme des ventes par client
    top_clients= df.groupby('full_name')['total'].sum().sort_values(ascending=False).head(10)

    # Création du barplot
    fig3 = px.bar(
        x=top_clients.values,
        y=top_clients.index,
        orientation='h',
        text=top_clients.values,
        labels={'x': 'Montant', 'y': 'Client'},
        color=top_clients.values,
        color_continuous_scale='Tealgrn'
    )
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)




col3, col4 = st.columns(2)

# 📊 Histogramme des âges
with col3:
    st.subheader("Répartition de l’âge des clients")
    fig5 = px.histogram(
        df,
        x="age",
        nbins=10,
        text_auto=True,
        color_discrete_sequence=['skyblue']
    )

    fig5.update_layout(
        xaxis_title="Âge",
        yaxis_title="Nombre de clients",
        bargap=0.1
    )
    st.plotly_chart(fig5, use_container_width=True)

# Diagramme de genre (hommes/femmes)
with col4:
    st.subheader("Répartition par Genre")

    # Compter le nombre d’hommes et de femmes
    genre_counts = df['Gender'].value_counts()
    total = genre_counts.sum()
    genre_percentages = (genre_counts / total * 100).round(1)

    genre_df = genre_counts.reset_index()
    genre_df.columns = ['Genre', 'Nombre']
    genre_df['Pourcentage'] = genre_percentages.values

    # Création du barplot
    fig6 = px.bar(
        genre_df,
        x="Genre",
        y="Nombre",
        text=genre_df.apply(lambda row: f"{row['Nombre']} ({row['Pourcentage']}%)", axis=1),
        color="Genre",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig6.update_traces(textposition="outside")
    fig6.update_layout(
        xaxis_title="Genre",
        yaxis_title="Nombre de clients",
        showlegend=False
    )

    st.plotly_chart(fig6, use_container_width=True)




st.subheader("Nombre de vente par mois")

# Créer deux colonnes : pour l'affichage et pour le tri
df['Mois_Annee_affichage'] = df['order_date'].dt.strftime('%b %Y')  # ex: Jan 2024
df['Mois_Annee_tri'] = df['order_date'].dt.to_period('M').astype(str)

# Grouper par mois-année tri
ventes_par_mois = df.groupby('Mois_Annee_tri').size().reset_index(name='Total_ventes')

# Ajouter la version affichable pour les labels
ventes_par_mois['Mois_Annee_affichage'] = pd.to_datetime(ventes_par_mois['Mois_Annee_tri']).dt.strftime('%b %Y')

# Trier par date réelle
ventes_par_mois['Mois_Annee_date'] = pd.to_datetime(ventes_par_mois['Mois_Annee_tri'])
ventes_par_mois = ventes_par_mois.sort_values('Mois_Annee_date')

# Tracer la courbe
fig7 = px.line(
    ventes_par_mois,
    x='Mois_Annee_affichage',
    y='Total_ventes',
    markers=True,
    title="Nombre total de ventes par mois"
)
fig7.update_xaxes(tickangle=45)
st.plotly_chart(fig7)


# Question 8

st.subheader("Le nombre total de vente par state")
dfstate = pd.read_csv('state_us_gps.csv')
dfstate = dfstate.rename(columns={'State': 'State_complet'})
ventes_par_state = df.groupby('State_complet').agg(
Total_ventes=('State', 'count'),
Chiffre_affaires=('total', 'sum')
).reset_index()

    # 2. Fusion avec dfstate (qui contient les coordonnées)
ventes_geo = ventes_par_state.merge(dfstate, on='State_complet', how='left')

    # 3. Retirer les États sans coordonnées (juste au cas où)
ventes_geo = ventes_geo.dropna(subset=['Latitude', 'Longitude'])

    # 4. Tracer la carte interactive
fig = px.scatter_map(
    ventes_geo,
    lat="Latitude",
    lon="Longitude",
    size="Total_ventes",
    color="Total_ventes",
    hover_name="State_complet",
    hover_data={
        "Chiffre_affaires": ":,.0f",        # format chiffre
        "Latitude": False,
        "Longitude": False
    },
    color_continuous_scale="Plasma",
    zoom=3,
    height=600
)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)




# Segmentation RFM
# Date de référence pour calculer la récence (la plus récente commande)
# Date de référence pour calculer la récence (la plus récente commande)
date_reference = df['order_date'].max()

# RFM par client
rfm = df.groupby('cust_id').agg({
    'order_date': lambda x: (date_reference - x.max()).days,  # Récence
    'cust_id': 'count',                                        # Fréquence
    'total': 'sum'                                             # Montant
}).rename(columns={
    'order_date': 'Recence',
    'cust_id': 'Frequence',
    'total': 'Montant'
}).reset_index()


# Calcul des seuils de percentiles
rfm['R'] = pd.qcut(rfm['Recence'], 5, labels=[5, 4, 3, 2, 1])
rfm['F'] = pd.qcut(rfm['Frequence'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M'] = pd.qcut(rfm['Montant'], 5, labels=[1, 2, 3, 4, 5])

rfm['RFM'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)


def segment_rfm(score):
    r, f, m = list(score)
    r = int(r)
    f = int(f)
    m = int(m)

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal"
    elif r >= 3 and (f <= 2 or m <= 2):
        return "Potentiel"
    elif r == 2:
        return "À réveiller"
    else:
        return "À risque"
rfm['Segment'] = rfm['RFM'].apply(segment_rfm)
df = df.merge(rfm[['cust_id', 'RFM', 'Segment']], on='cust_id', how='left')
# st.dataframe(df)
st.write("")
st.markdown("---")
st.subheader("Segmentation par recence, frequence et montant(RFM)")
st.dataframe(rfm.head())

col1, col2 = st.columns(2)

# === Diagramme circulaire : Répartition des segments ===
with col1:
    st.subheader("Répartition des segments RFM")
    
    # Compter les segments
    segment_counts = df.drop_duplicates(subset='cust_id')['Segment'].value_counts()
    labels = segment_counts.index
    sizes = segment_counts.values

    # Création du camembert
    fig = px.pie(
    names=labels,        # les catégories
    values=sizes,        # les valeurs
    hole=0,              # =0 → camembert plein ; =0.4 → donut
    )

    # Options supplémentaires pour ressembler à ton code Matplotlib
    fig.update_traces(textinfo='percent+label')   # afficher % et labels
    st.plotly_chart(fig, use_container_width=True)

# Diagramme en barres : Montant total par segment
with col2:
    st.subheader("Montant total généré par segment")
    # Regrouper les montants par segment
    montant_par_segment = df.groupby('Segment')['total'].sum().sort_values(ascending=False)

    # Créer un DataFrame pour Plotly
    df_plot = montant_par_segment.reset_index()
    df_plot.columns = ["Segment", "Montant"]

    # Graphique interactif
    fig2 = px.bar(
        df_plot,
        x="Segment",
        y="Montant",
        text=df_plot["Montant"].apply(lambda v: f"${v:,.0f}"),  # valeurs formatées avec $
        labels={"Montant": "Montant total", "Segment": "Segment"},
        color="Montant",
        color_continuous_scale="Tealgrn"
    )

    # Options
    fig2.update_traces(textposition="outside")
    fig2.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Treemap")
df_unique = df.drop_duplicates(subset=["cust_id"])
fig8 = px.treemap(
    df_unique,
    path=["Region", "Segment"],
    color="Segment"
)
st.plotly_chart(fig8, use_container_width=True)

