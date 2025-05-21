
import pandas as pd
from io import StringIO

# Sample data
data = 'Airline Code;DelayTimes;FlightCodes;To_From\nAir Canada (!);[21, 40];20015.0;WAterLoo_NEWYork\n<Air France> (12);[];;Montreal_TORONTO\n(Porter Airways. );[60, 22, 87];20035.0;CALgary_Ottawa\n12. Air France;[78, 66];;Ottawa_VANcouvER\n""".\\.Lufthansa.\\.""";[12, 33];20055.0;london_MONTreal\n'

def fill_flight_codes_step(df, col='FlightCodes', step=10):
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors='coerce')

    non_NaN = df[col].dropna() # Get the non-NaN values

    #if all values are NaN, fill with step starting from 0, (potential edge case)
    if non_NaN.empty:   
        df[col] = pd.Series(range(0, step * len(df), step), index=df.index) 
        return df


    anchor_idx = non_NaN.index[0] 
    anchor_val = non_NaN.iloc[0]

    #create a sequence based on the anchor value and the step size
    seq = pd.Series(data = anchor_val + (df.index - anchor_idx) * step, index=df.index) 

    # Assign to the column, as an integer value
    df[col] = seq.astype(int) 
    return df


def clean_up(data):
    # Read the data into a DataFrame
    df = pd.read_csv(StringIO(data), sep=";")

    # Clean 'Flight Codes', using step size to fill in missing values, even for cases where all values are NaN
    # You can also use df['FlightCodes'].interpolate(method='linear', limit_direction='both') to fill in the missing values with linear interpolation but to gaurantee the step size, I will use a custom function.
    df = fill_flight_codes_step(df, col='FlightCodes', step=10) # fill in the missing values with linear interpolation

    # Split 'To_From' into 'To' and 'From' columns, handle missing delimiters
    splits = df['To_From'].str.split('_', n=1, expand=True)
    splits = splits.reindex(columns=[0, 1], fill_value='') # fill with empty string for edge cases where the to and from does not have a delimiter (turning around a flight back to the same city, or a flight to the same city)
    df['To']   = splits[0].str.strip().str.upper()
    df['From'] = splits[1].str.strip().str.upper().fillna('') 
    df.drop(columns=['To_From'], inplace=True) # drop the To_From column


    # Clean 'Airline Code': strip spaces, remove special characters, and title-case
    df['Airline Code'] = df['Airline Code'].str.strip() # remove any leading or trailing spaces
    df['Airline Code'] = df['Airline Code'].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True) # remove any special characters with a empty character
    df['Airline Code'] = df['Airline Code'].str.title() # convert to title case

    return df


print(clean_up(data))