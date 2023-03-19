import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from fit_file import read

fit_dir = "data/hok_klubmesterskab_2022/CA8D1347.FIT"
control_time_data_dir = "data/hok_klubmesterskab_2022/kontroltider.csv"

pd.set_option('display.max_rows', None)


# Gets data form sources
def get_data():
    
    fit_datalist = pd.DataFrame(read.read_points(fit_dir))
    
    controltime_datalist = pd.read_csv(control_time_data_dir, parse_dates=['timestamp'])
    
    return fit_datalist, controltime_datalist


# Matches controlpoints to find the closets point form fit datalist and adds to mathc dataframe
def match_times(controltime_datalist, fit_datalist):
    matched_points = []

    for _, control_point in controltime_datalist.iterrows():
        closest_fit_point = fit_datalist.loc[(fit_datalist['timestamp'] - control_point['timestamp']).abs().idxmin()]

        matched_points.append({
            'control_timestamp': control_point['timestamp'],
            'control_nr': control_point['nr'],
            'fit_timestamp': closest_fit_point['timestamp'],
            'latitude': closest_fit_point['latitude'],
            'longitude': closest_fit_point['longitude'],
            'altitude': closest_fit_point['altitude'],
            'heart_rate': closest_fit_point['heart_rate'],
            'cadence': closest_fit_point['cadence']
        })

    return pd.DataFrame(matched_points)

def get_entries_between_all_control_points(matched_df):
    result = pd.DataFrame()
    control_points = matched_df['control_nr'].unique()
    total_ran = 0

    for i in range(len(control_points) - 1):
        start_control_nr = control_points[i]
        end_control_nr = control_points[i + 1]

        start_timestamp = matched_df.loc[matched_df['control_nr'] == start_control_nr, 'control_timestamp'].iloc[0]
        end_timestamp = matched_df.loc[matched_df['control_nr'] == end_control_nr, 'control_timestamp'].iloc[0]

        entries_between = fit_datalist[(fit_datalist['timestamp'] >= start_timestamp) & (fit_datalist['timestamp'] <= end_timestamp)]
        entries_between = entries_between.assign(start_control_nr=start_control_nr, end_control_nr=end_control_nr)


        result = pd.concat([result, entries_between], ignore_index=True)

    # Include entries after the last control point
    last_control_nr = control_points[-1]
    last_timestamp = matched_df.loc[matched_df['control_nr'] == last_control_nr, 'control_timestamp'].iloc[0]
    entries_after_last = fit_datalist[fit_datalist['timestamp'] >= last_timestamp]
    entries_after_last = entries_after_last.assign(start_control_nr=last_control_nr, end_control_nr='finish')


    result = pd.concat([result, entries_after_last], ignore_index=True)

    return result


def get_distance(df):
    uniques = df["start_control_nr"].unique()
    result = pd.DataFrame()
    threshold_speed = 1.5 
    control_distance = 0

    walk_distance = 0
    run_distance = 0

    for start_control_nr in uniques:
        filtered_df = df[df['start_control_nr'] == str(start_control_nr)]
        
        prev_lat, prev_lon = None, None
        
        prev_row = None
        
        for _, row in filtered_df.iterrows():
            lat1, lon1 = radians(row['latitude']), radians(row['longitude'])

            if prev_lat is not None and prev_lon is not None:
                dist = distance({'latitude': prev_lat, 'longitude': prev_lon}, {'latitude': lat1, 'longitude': lon1})
                dt = (row['timestamp'] - prev_row['timestamp']).seconds
                if dt == 0:
                    v = 0
                else:
                    v = dist / dt
                if v < threshold_speed:
                    walk_distance += dist
                else:
                    run_distance += dist

                control_distance += dist
            
            prev_row = row
            prev_lat, prev_lon = lat1, lon1 
            

        filtered_df['distance M'] = control_distance
        filtered_df['walking M'] = walk_distance
        filtered_df['run M'] = run_distance

        percentage_walked = round((run_distance / control_distance) * 100)
        filtered_df['percentage_run'] = percentage_walked

        # Get the last row of the filtered_df DataFrame and add it to the result DataFrame
        result = pd.concat([result, filtered_df.tail(1)], ignore_index=True)

    print(result)
    return result



# Haversine formula 
# Calculates the distance between to points (lat, lon)
def distance(point1, point2):
    R = 6371000.0

    lat1, lon1 = point1['latitude'], point1['longitude']
    lat2, lon2 = point2['latitude'], point2['longitude']

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c



if __name__ == "__main__":
    # Usage example
    fit_datalist, controltime_datalist = get_data()
    matches = match_times(controltime_datalist, fit_datalist)
    entries = get_entries_between_all_control_points(matches)
    
    get_distance(entries)