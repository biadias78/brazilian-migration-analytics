import os
import streamlit as st
import duckdb
import pandas as pd
import joblib

st.title("Education Outflow Prediction")
st.write("A simple Streamlit app to predict migration outflow based on education features.")

con = duckdb.connect('duckdb/brazil_migration.duckdb')

@st.cache_data
def load_data():
    query = '''
    select year, education_group, total_migrants, male_ratio, female_ratio
    from dim_brazil_education_features
    '''
    return con.execute(query).df()

@st.cache_resource
def load_model():
    model_path = 'models/prediction_model.pkl'
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

data = load_data()
model = load_model()

st.subheader('Historical education outflow')
st.dataframe(data.head(20))

st.subheader('Prediction inputs')
education_group = st.selectbox('Education group', ['high education', 'medium education', 'low education'])
male_ratio = st.slider('Male ratio', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
female_ratio = st.slider('Female ratio', min_value=0.0, max_value=1.0, value=0.5, step=0.01)

education_group_map = {
    'high education': 1,
    'medium education': 0,
    'low education': 2,
}

user_input = pd.DataFrame([
    {
        'education_group': education_group_map[education_group],
        'male_ratio': male_ratio,
        'female_ratio': female_ratio,
    }
])

if st.button('Predict'):
    prediction = model.predict(user_input)
    st.write(f'Predicted total migrants: {prediction[0]:.0f}')

st.write('---')
st.write('Data preview from dim_brazil_education_features')
st.dataframe(data)
