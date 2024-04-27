from dash import Dash, html, callback, clientside_callback, Output, Input, State
import dash_bootstrap_components as dbc
from function import *
import pandas as pd

# The logo path
DFA_LOGO = '/assets/logo.png'

# To get the stopword list
stopwords_list = get_stopwords()

# To create the DFA for all stopwords
DFA = StopwordDFA(stopwords_list)

# The navigation bar at the top of the website
navbar = dbc.Navbar(

    html.Div(
        [

            # The logo with website title
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            html.Img(src=DFA_LOGO),
                            style={'backgroundColor': 'white'},
                            className='rounded-circle p-2'
                        ),

                    ),
                    dbc.Col(dbc.NavbarBrand("Stopword DFA", className="ms-2 fw-bold fs-3")),
                ],
                align="center",
                className="g-0",
            ),

        ],
        className='ms-3'
    ),
    color="primary",
    dark=True,
    style={'height': '15vh'}
)

# The first tab content displaying each word's result
tab1_content = dbc.Card(
    dbc.CardBody([
        html.Div([
            dbc.ListGroup(id='resultLogs')
        ],
            style={'width': '25vw', 'maxHeight': '48vh', 'overflowY': 'auto'}
        )
    ],
        className='d-flex justify-content-center'
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='resultText', style={'maxHeight': '48vh', 'overflowY': 'auto'})
    ]),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody([
        html.Div(id='stopwordOccurrencesTable',
                 style={'width': '25vw', 'maxHeight': '48vh', 'overflowY': 'auto'})
    ],
        className='d-flex justify-content-center'
    ),
    className="mt-3",
)

''''''''''''''''''''''''''''''''''''''''''''''The main Dash app'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# The dash app with its title and theme:https://bootswatch.com/ (For theme options)
app = Dash(__name__, title='Stopword DFA',
           external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP, '/assets/styles.css'])

# The dash layout - all the html like button inside it (showing in website)
app.layout = html.Div([
    # The navbar define above
    navbar,

    # The content divide into columns
    html.Div([
        dbc.Row([

            # The stopwords list
            dbc.Col(
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                html.Div([
                                    html.Ul([html.Li(word) for word in stopwords_list])
                                ], style={'maxHeight': '72vh', 'overflowY': 'auto'})
                            ],
                            title="Stopwords",
                            className='bg-light'
                        )
                    ],
                ),
                width=2,
            ),

            # The main content
            dbc.Col([
                html.Div([

                    # First page (input)
                    html.Div([
                        html.Div([

                            # The card containing the textarea input
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("Input Text", className="card-title"),
                                    dbc.Textarea(id='textInput', className="mb-3", value='', rows=10,
                                                 placeholder="Please provide your input here.\n"
                                                             "Hint: Press Shift + Enter to move to the next line."),
                                ])
                            ],
                                className='w-75 bg-light mt-5'
                            ),
                        ],
                            className='d-flex justify-content-center'
                        ),

                        # The check button
                        html.Div(
                            dbc.Button("Check Stopword", id='checkButton', color="primary", size='lg'),
                            className="d-flex justify-content-center mt-3"
                        )
                    ],
                        id='inputPage'
                    ),

                    html.Div([
                        dbc.Button('<< Back', id='backButton', color='info', className='mb-3'),

                        dbc.Tabs([
                            dbc.Tab(tab1_content, label="Result Logs", activeTabClassName="fw-bold fst-italic",
                                    activeLabelClassName="text-primary", tab_id='tab1'),
                            dbc.Tab(tab2_content, label="Result Text", activeTabClassName="fw-bold fst-italic",
                                    activeLabelClassName="text-primary"),
                            dbc.Tab(tab3_content, label="Stopword Occurrences", activeTabClassName="fw-bold fst-italic",
                                    activeLabelClassName="text-primary"),
                        ], id='tabs')
                    ],
                        id='resultPage', className='p-5', hidden=True
                    )

                ],
                    style={'height': '85vh'},
                    className='border-start border-bottom'
                )

            ]),
        ],
            className='g-0')
    ])
])

# To check the input, if it has input, then enable the button and change the hover effect
# Else, disabled the button
clientside_callback(
    """
    function(value) {
        if (value.trim().length > 0) {
            return false;
        } else {
            return true;
        }
    }
    """,
    Output('checkButton', 'disabled'),
    Input('textInput', 'value')
)


# To create a success log for frontend
def createSuccessLog(word):
    return dbc.ListGroupItem([
        html.Div([
            html.Div([
                html.I(className="bi bi-check-circle-fill me-2"),
                html.Span(word)
            ]),

            dbc.Badge(
                "Accept",
                color="success",
                className="border me-1",
            )
        ],
            className='d-flex justify-content-between align-items-center'
        )],
        color="success"
    )


# To create a fail log for frontend
def createFailLog(word):
    return dbc.ListGroupItem([
        html.Div([
            html.Div([
                html.I(className="bi bi-x-circle-fill me-2"),
                html.Span(word)
            ]),

            dbc.Badge(
                "Reject",
                color="danger",
                className="border me-1",
            )
        ],
            className='d-flex justify-content-between align-items-center'
        )],
        color="danger"
    )


# To display the original text with highlighted stopwords
def highlight_stopwords(found_stopword, text):
    # Split the text into multi lines of text
    text_lines = text.splitlines()

    # As a div to store all the text that will be displayed in frontend
    full_text = []

    # For each line of text
    for line in text_lines:

        # If the line has words
        if line:
            # Replace the space between words to _SPACE_ to avoid the space be removed when tokenization
            line = re.sub(r'\s', ' _SPACE_ ', line)

            # Tokenize the text
            tokens = tokenize(line)

            # It stores the html elements for each line
            paragraph = []

            # To store the string that will be added in a html <span>
            formatted_line = ""

            # For each token (word)
            for token in tokens:

                # Maybe there are stopword in capital letter, and stopword list is in lowercase,
                # so convert to lowercase when checking it is stopword or not.
                # If it is stopword
                if token.lower() in found_stopword:

                    # Check the formatted line has contents or not, if it has then added to paragraph first
                    if formatted_line:
                        paragraph.append(html.Span(formatted_line))

                    # Then add html span for the stopword with highlight
                    paragraph.append(html.Span(token, className='fw-bold', style={'color': 'black'}))
                    formatted_line = ""

                else:

                    # If it is space, add to the formatted_line as normal space
                    if token == "_SPACE_":
                        formatted_line += " "

                    # Or add the word
                    else:
                        formatted_line += token

            # Once all the words in a line finish, then add the last formatted_line, and as html <p> in full_text
            paragraph.append(html.Span(formatted_line))
            full_text.append(html.P(paragraph))

        # If the line don't have any word, means it is a empty line, then add new line
        else:
            full_text.append(html.Br())

    return full_text


# To create a table for the stopword occurrences
def createStopwordOccurrenceTable(stopword_occurrences):
    # Convert dictionary to DataFrame
    df = pd.DataFrame(list(stopword_occurrences.items()), columns=['Stopword', 'Occurrences'])

    # USe df to create the table
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, color='primary',
                                    responsive=True, style={'textAlign':'center'})


# To process the input text when clicking the button
# The show the result page with the result
@callback(
    Output('inputPage', 'hidden'),
    Output('resultPage', 'hidden'),
    Output('resultLogs', 'children'),
    Output('resultText', 'children'),
    Output('stopwordOccurrencesTable', 'children'),
    Input('checkButton', 'n_clicks'),
    State('textInput', 'value'),
    prevent_initial_call=True,
    running=[(Output("checkButton", "disabled"), True, False)]
)
def checkStopwords(n, text):
    # Preprocess the text before doing DFA
    tokens = preprocess_words(text)

    # Initialize an empty list to store the results
    logs = []
    found_stopword = {}

    for word in tokens:
        if DFA.is_stopword(word):
            logs.append(createSuccessLog(word))

            if word in found_stopword:
                found_stopword[word] += 1
            else:
                found_stopword[word] = 1

        else:
            logs.append(createFailLog(word))

    # Sort the dictionary of stopword occurrences in ascending order
    found_stopword = dict(sorted(found_stopword.items()))

    # To get the text with highlighted stopwords
    highlighted_text = highlight_stopwords(list(found_stopword.keys()), text)

    # To create table for stopword occurrences
    table = createStopwordOccurrenceTable(found_stopword)

    return [True, False, logs, highlighted_text, table]


# The back button callback
@callback(
    Output('inputPage', 'hidden', allow_duplicate=True),
    Output('resultPage', 'hidden', allow_duplicate=True),
    Output('tabs', 'active_tab'),
    Input('backButton', 'n_clicks'),
    prevent_initial_call=True,
)
def goBackInputPage(n):
    return [False, True, 'tab1']


# To run the dash app
if __name__ == '__main__':
    app.run(debug=False)
