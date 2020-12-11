#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import ipywidgets as widgets
from ipywidgets import Button, Layout, Textarea, HBox, VBox
import io
import base64
import datetime


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import dash_table


import plotly.graph_objs as go
from flask import Flask


# In[ ]:


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df = df.drop_duplicates()
            df["ACCUSER"] = np.random.choice([True, False], p=[0.0, 1.0], size=len(df))
            df['NUM_CASES'] = df.groupby('REF_ID')['REF_ID'].transform('count')
            df['NUM_ASM_MALTREATMENT'] = df['ASM_MALTREATMENT'].apply(str).apply(lambda n: len(n.split(',')))
            df['ABUSER'] = "Parent"
            df["Drug/Violent History"] = np.random.choice([True, False], p=[0.0, 1.0], size=len(df))
            
            def decision(df):
                if df["ACCUSER"] == True:
                    return "High Priority Case"
                elif (df["AGE"] < 4 or df["AGE"] == 0) and df["NUM_CASES"] > 2:
                    return "High Priority Case"
                elif (df['AGE'] < 4 or df['AGE'] == 0) and df["NUM_ASM_MALTREATMENT"] > 1:
                    return "High Priority Case"
                elif (df['AGE'] < 4 or df['AGE'] == 0) and (df["ABUSER"] == "Parent") and df["Drug/Violent History"] == True:
                    return "High Priority Case"
                elif (df["AGE"] > 3 and df["AGE"] < 9) and df["NUM_CASES"] > 2:
                    return "High Priority Case"
                elif (df["AGE"] > 3 and df["AGE"] < 9) and (df["NUM_ASM_MALTREATMENT"] > 1) and (df["ABUSER"] == "Parent"):
                    return "High Priority Case"
                elif (df["AGE"] > 8) and (df["NUM_CASES"] > 2) and (df["NUM_ASM_MALTREATMENT"] > 1):
                    return "High Priority Case"
                else:
                    return "Lower Priority Case"
                
                
            screen = df.apply(lambda df : decision(df), axis=1)
            screen = screen.to_frame()
                
            app_df = df.join(screen, how='outer')
            app_df2 = app_df.rename(columns={0: 'Priority'})
                
            
    except Exception as e:
        print(e)
        return html.Div([
            'File must be a CSV'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=app_df2.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in app_df2.columns],
            export_format="csv",
            
            
            
            
            
            
            
            
            sort_action= 'native',
            editable=True,
            style_data_conditional=[
        {
            'if': {

                'filter_query': '{Priority} contains "High Priority Case"',
                'column_id': 'Priority'
            },
            'backgroundColor': '#85144b',
            'color': 'white'
        }
    ]
        
        
        ),
       

        
        
        
        
        
        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



if __name__ == '__main__':
#    app.run_server(debug=True)
    app.run_server(port=8050,host='0.0.0.0')


# In[ ]:


# view at http://localhost:8050/


# In[ ]:




