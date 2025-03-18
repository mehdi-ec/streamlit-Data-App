import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import matplotlib.dates as mdates
import plotting


# Set the page config
st.set_page_config(page_title='Data Visualizer',
                   layout='centered',
                   page_icon='📊')

# Title
st.title('📊  Data Visualizer')

working_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the folder where your CSV files are located
folder_path = f"{working_dir}/data"  # Update this to your folder path

# List all files in the folder
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Dropdown to select a file
selected_file = st.selectbox('Select a file', files, index=None)

if selected_file:
    # Construct the full path to the file
    file_path = os.path.join(folder_path, selected_file)

    # Read the selected CSV file
    df = pd.read_csv(file_path)

    columns = df.columns.tolist()

    st.write("")

    st.header("Data Preview")

    head_df = df.head()
    dtypes_series = df.dtypes

    # Create a new row with the data types
    dtypes_row = pd.Series(dtypes_series.values, index=head_df.columns, name="Type")

    # Concatenate the head DataFrame and the data types row
    combined_df = pd.concat([pd.DataFrame(dtypes_row).T,head_df])

    st.write(combined_df)


    ##################################################################################


    import pandas as pd

    # Assuming df is your pandas DataFrame and columns is a list of column names
    st.header('Changing the Type')


    # Initialize lastState in session state
    if 'lastState' not in st.session_state:
        st.session_state.lastState = None  # Default to None initially

    # ⚠️ Display lastState only if changes were made
    if st.session_state.lastState is None:
        st.warning("⚠️ In order to make changes: select the column(s) and desired type then confirm ")  # Updated warning message


    # Adjust column width to align button correctly with dropdowns
    col1, col2, col3 = st.columns([3, 3, 1.5])  # Adjusted button column width

    # Initialize session state for df_dtypes if not already present
    if 'df_dtypes' not in st.session_state:
        st.session_state.df_dtypes = df.dtypes.to_dict()  # Initialize with current dtypes



    # Column selection
    with col1:
        choose_cols = st.multiselect('Change the type of specific columns', options=columns)

    # Type selection with default empty value if user hasn't made input yet
    with col2:
        possible_types = ['int64', 'float64', 'bool', 'datetime64[ns]', 'timedelta64[ns]', 'category']
        choose_type = st.selectbox('Set type to:', options=[""] + possible_types, index=0)  # Default empty

    # Fix button alignment and add controlled spacing
    with col3:
        st.markdown("<div style='margin-bottom: 6px; font-weight: bold;'>Confirm</div>", unsafe_allow_html=True)  # Adjusted spacing
        change_type_clicked = st.button("Change Type")  # Button right under the text



    # Ensure both column(s) and type are selected
    if choose_cols and choose_type and change_type_clicked:
        try:
            for col in choose_cols:
                if choose_type == 'category':
                    df[col] = df[col].astype('category')
                else:
                    df[col] = df[col].astype(choose_type)

                # Update session state with the new dtype
                st.session_state.df_dtypes[col] = choose_type

            # ✅ Show success message when type change is confirmed
            st.success(f"✅ Column(s) '{', '.join(choose_cols)}' type successfully changed to '{choose_type}'.")

            # Create a new row with the updated data types
            dtypes_series = pd.Series(st.session_state.df_dtypes)
            dtypes_row = pd.Series(dtypes_series.values, index=head_df.columns, name="Type")

            # Concatenate the head DataFrame and the data types row
            combined_df = pd.concat([pd.DataFrame(dtypes_row).T, head_df])

            # Store in session state to persist across reruns
            st.session_state.lastState = combined_df

        except ValueError as e:
            st.error(f"❌ Error changing type: {e}")
        except TypeError as e:
            st.error(f"❌ Error changing type: {e}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")

    # ✅ Display lastState only if changes were made
    if st.session_state.lastState is not None:
        st.markdown("**📊 Updated table**")  # Bold heading with emoji
        st.write(st.session_state.lastState)


    ##################################################################################
    # Create Visualisation 
    st.header('Creating Visualisations')

        # Assuming df is your pandas DataFrame and columns is a list of column names

    if 'df_dtypes' not in st.session_state:
        st.session_state.df_dtypes = df.dtypes.to_dict()  # Initialize with current dtypes

    # Allow the user to select columns for plotting
    x_axis = st.selectbox('Select the X-axis', options=columns + ["None"])
    y_axis = st.selectbox('Select the Y-axis', options=columns + ["None"])

    plot_list = []  

    if x_axis != "None" and y_axis != "None":
        # Get dtypes from session state, or default to df.dtypes if not available
        x_dtype = st.session_state.df_dtypes.get(x_axis, df[x_axis].dtype)
        y_dtype = st.session_state.df_dtypes.get(y_axis, df[y_axis].dtype)

        if x_dtype == 'category' and (y_dtype == 'int64' or y_dtype == 'float64'):
            plot_list.append('Bar Chart')  # Add Bar Chart if conditions are metplot_list.append('Bar Chart') 
            plot_list.append('Pie Chart') 
            plot_list.append('Box Chart') 

        elif (x_dtype == 'int64' or x_dtype == 'float64') and (y_dtype == 'int64' or y_dtype == 'float64'):
            plot_list.append('Scatter Plot')  
            plot_list.append('Line Chart')  

        elif (x_dtype == 'datetime64[ns]' ):
            plot_list.append('Line Chart')  


    # If none have been selected, reset the plot list.
    if x_axis == "None" or y_axis == "None":
        plot_list = ['Line Chart', 'Scatter Plot', 'Distribution Plot', 'Count Plot']

    plot_type = st.selectbox('Select the type of plot', options=plot_list)


    # Generate the plot based on user selection
    if st.button('Generate Plot'):

        fig, ax = plt.subplots(figsize=(6, 4))


        if plot_type == 'Bar Chart':
            sns.barplot(x=df[x_axis], y=df[y_axis], ax=ax)
        elif plot_type == 'Box Chart':
            sns.boxplot(x=df[x_axis], y=df[y_axis], ax=ax)  
        elif plot_type == "Pie Chart":
            pie_data = df.groupby(x_axis)[y_axis].sum()  # Aggregate values
            ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))

        elif plot_type == 'Line Chart':
            if(x_dtype == 'datetime64[ns]'):
                plotting.create_lineChart_Date(df,x_axis,y_axis,ax)
            else:
                sns.lineplot(x=df[x_axis], y=df[y_axis], ax=ax)
        elif plot_type == 'Scatter Plot':
            sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax)


        elif plot_type == 'Distribution Plot':
            sns.histplot(df[x_axis], kde=True, ax=ax)
            y_axis='Density'
        elif plot_type == 'Count Plot':
            sns.countplot(x=df[x_axis], ax=ax)
            y_axis = 'Count'


                   
        # Adjust label sizes
        ax.tick_params(axis='x', labelsize=10)  # Adjust x-axis label size
        ax.tick_params(axis='y', labelsize=10)  # Adjust y-axis label size

        # Adjust title and axis labels with a smaller font size
        plt.title(f'{plot_type} of {y_axis} vs {x_axis}', fontsize=12)
        plt.xlabel(x_axis, fontsize=10)
        plt.ylabel(y_axis, fontsize=10)

        # Show the results
        st.pyplot(fig)
