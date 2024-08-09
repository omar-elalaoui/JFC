
import plotly.graph_objs as go
import pandas as pd 
from dash import Dash, html, dcc, Output, Input
import plotly.express as px

app = Dash(__name__)


inputs = {
    "Débit massique de la pulpe sortie thickener": ["J_AFC_PHOS_DEBIT_MASSIQUE_B"],
    "Débit volumique de  de la pulpe sortie thikner  thickener":[
        "J_AFC_PHOS_402AFIC192M_B", "J_AFC_PHOS_402AFIC186M_B", "J_AFC_PHOS_402AFIC180M_B"
    ],
    "Densité pulpe sortie  thickener":[
        "J_AFC_PHOS_402ADIC193_B", "J_AFC_PHOS_402ADIC187_B", "J_AFC_PHOS_402ADIC181_B"
    ],
    
    "Débit acide sulfurique": ["J_AFC_PHOS_SIGMA-FI-SA_B"],
    # "Débit acide recyclé (FA)": ["Débit acide recyclé (FA)"],
    "Débit acide recyclé (FB)": ["J_AFC_PHOS_403AFIC832_B"],
    "Débit des boues 29A vers a CA": ["J_AFC_PHOS_413AFIC066_B"],
    "Débit des boues  29B vers a CA ": ["J_AFC_PHOS_403AFIC026_B"],
    "Débit eau de lavage filtre (FA)": ["J_AFC_PHOS_403AFI770A_B"],
    "Débit eau de lavage filtre (FB)": ["J_AFC_PHOS_403AFI870B_B"]
}

global_data = "644451721849352_data JFC1.xlsx"
jfc1 = pd.read_excel(global_data, header=1, engine='openpyxl')

# Ensure 'Unnamed: 0' is datetime
jfc1['Unnamed: 0'] = pd.to_datetime(jfc1['Unnamed: 0'])

# Get unique dates
unique_days = jfc1['Unnamed: 0'].dt.date.drop_duplicates().sort_values()

# Define app layout
app.layout = html.Div([
    html.H1(children='JFC1 Analytics', style={'textAlign':'center', 'padding': '20px'}),
    html.Div([
        dcc.Dropdown(
            options=[{'label': key, 'value': key} for key in inputs.keys()],
            id='dropdown-selection',
            placeholder="Select an input",
            style={'width': '30%', 'display': 'inline-block', 'marginRight': '10px'}
        ),
        dcc.Dropdown(
            options=[{'label': key, 'value': key} for key in inputs.keys()],
            id='dropdown-selection2',
            placeholder="Select an input",
            style={'width': '30%', 'display': 'inline-block', 'marginRight': '10px'}
        ),
        dcc.Dropdown(
            options=[{'label': str(date), 'value': str(date)} for date in unique_days],
            id='dates',
            placeholder="Select a date",
            style={'width': '30%', 'display': 'inline-block'}
        )
    ]),
    html.Div([
        dcc.Graph(id='graph-content', style={'display': 'inline-block'}),
        dcc.Graph(id='graph-content2', style={'display':'inline-block'})
    ]),
    html.H1(children='JFC1 Analytics lab', style={'textAlign':'center', 'padding': '20px'}),
    # dcc.Dropdown(
    #     options=[{'label': key, 'value': key} for key in date_dict.keys()],
    #     id='dropdown-selection3',
    #     placeholder="Select an input"
    # ),
    dcc.Graph(id='graph-content3')
    
], style={'padding': '30px'})

# Define callback function
@app.callback(
    [Output('graph-content', 'figure'), Output('graph-content2', 'figure'), Output('graph-content3', 'figure') ],
    [Input('dropdown-selection', 'value'), Input('dropdown-selection2', 'value'), Input('dates', 'value')]
)
def update_graph(selected_input, selected_input2, selected_date):
    if selected_input is None or selected_date is None:
        return px.line(), px.line(), px.line() # Return an empty figure if no input or date is selected
    
    try:
        # Get the list of columns for the selected input
        columns = inputs[selected_input]
        
        # Convert selected_date back to datetime.date
        selected_date = pd.to_datetime(selected_date).date()
        
        # Filter data for the selected date
        selected_data = jfc1[jfc1['Unnamed: 0'].dt.date == selected_date]
        
        # Create a figure
        fig = go.Figure()
        
        # Add a line for each column
        for column in columns:
            fig.add_trace(go.Scatter(x=selected_data['Unnamed: 0'], y=selected_data[column], mode='lines', name=column))
        
        # Update layout
        fig.update_layout(
            title=f"{selected_input} on {selected_date}",
            xaxis_title='Time',
            yaxis_title='Value',
            xaxis_tickformat='%H:%M'  # Show only hours and minutes
        )
        
        columns2 = inputs[selected_input2]
        
        fig2 = go.Figure()
        for column in columns2:
            fig2.add_trace(go.Scatter(x=selected_data['Unnamed: 0'], y=selected_data[column], mode='lines', name=column))
        
        # Update layout
        fig2.update_layout(
            title=f"{selected_input2} on {selected_date}",
            xaxis_title='Time',
            yaxis_title='Value',
            xaxis_tickformat='%H:%M'  # Show only hours and minutes
        )
    

        lab_data = "consolidated_logfile.xlsx"
        analyse_labo = pd.read_excel(lab_data)
        analyse_labo['Date'] = pd.to_datetime(analyse_labo['Date'].astype(str) + ' ' + analyse_labo['Time'].astype(str))
        analyse_labo = analyse_labo[analyse_labo["Date"].dt.date == selected_date]

        fig3 = go.Figure()
        
        # Add a line for each column
        columns = [' Bouillie','Filtrat Bouillie', 'Sulfates libres']
        for column in columns:
            fig3.add_trace(go.Scatter(x=analyse_labo['Time'], y=analyse_labo[column], mode='lines', name=column))
        
        # Update layout
        fig3.update_layout(
            # title=f"{selected_input} on {selected_date}",
            xaxis_title='Time',
            yaxis_title='Value',
            xaxis_tickformat='%H:%M'  # Show only hours and minutes
        )

        # filtr_data["J_AFC_PHOS_402AFIC180M_B"] / filtr_data["J_AFC_PHOS_SIGMA-FI-SA_B"]


        
        return fig, fig2, fig3
    except Exception as e:
        print(f"Error: {e}")
        return px.line(), px.line(), px.line()  # Return an empty figure if there's an error



if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host="0.0.0.0")
