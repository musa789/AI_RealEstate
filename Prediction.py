import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# read the train data from the csv file
train_data = pd.read_csv('train_data.csv')

# extract relevant columns
train_data = train_data[['location_id', 'latitude', 'longitude', 'property_type', 'price', 'area', 'date_added']]

# preprocess the data by extracting numerical values from the date_added column
train_data['date_added'] = pd.to_datetime(train_data['date_added'])
train_data['date_added_num'] = train_data['date_added'].apply(lambda x: x.toordinal())

# train a linear regression model for each property type and location combination
property_types = train_data['property_type'].unique()
locations = train_data['location_id'].unique()

models = {}
for prop in property_types:
    models[prop] = {}
    for loc in locations:
        # get data for the current property type and location
        data = train_data[(train_data['property_type'] == prop) & (train_data['location_id'] == loc)]
        
        if len(data) == 0:
            continue
        
        # create X and y matrices for linear regression
        X = data[['date_added_num']].values
        y = data[['price']].values
        
        # train the linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        models[prop][loc] = model

# define the periods to predict
periods = [3, 6, 12, 24]

# create a list to store the predicted values for each property type and location combination
predictions = []

# predict the expected sales for each property type and location combination
for prop in property_types:
    for loc in locations:
        # get the model for the current property type and location
        model = models[prop].get(loc, None)
        
        if model is None:
            continue
        
        # get the latest date in the train dataset for the current property type and location
        max_date_num = train_data[(train_data['property_type'] == prop) & (train_data['location_id'] == loc)]['date_added_num'].max()
        
        # create a dataframe with the periods to predict
        pred_df = pd.DataFrame({'date_added_num': [max_date_num + 30 * p for p in periods]})
        
        # predict the expected sales for each period
        pred_df['price'] = model.predict(pred_df[['date_added_num']])
        pred_df['period'] = periods
        pred_df['property_type'] = prop
        pred_df['location_id'] = loc
        pred_df['latitude'] = train_data[train_data['location_id'] == loc]['latitude'].iloc[0]
        pred_df['longitude'] = train_data[train_data['location_id'] == loc]['longitude'].iloc[0]
        
        # append the predictions to the list
        predictions.append(pred_df)

# concatenate the predictions into a single dataframe
predictions_df = pd.concat(predictions, ignore_index=True)

# format the output dataframe
output_df = predictions_df[['latitude', 'longitude', 'property_type', 'period', 'price', 'location_id']]
output_df.columns = ['Latitude', 'Longitude', 'Property Type', 'Period', 'Expected Sales', 'Location ID']

# save the output dataframe to a csv file
output_df.to_csv('expected_sales.csv', index=False)
