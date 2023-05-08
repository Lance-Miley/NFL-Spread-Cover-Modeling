import pandas as pd
import numpy as np
from haversine import haversine, Unit

def summary_data(df, offense_column, defense_column, home_away_table, qtrs = 'N'):
    if defense_column != False:
        final_data = pd.DataFrame()
        groups = df.groupby(["team", "year"])
        for name, group in groups:
            offense_list = []
            defense_list = []
            df_t = pd.DataFrame(group)
            df_t = df_t.sort_values("week")
            num_of_games = df_t.shape[0]
            if qtrs == 'N':
                for i in range(num_of_games):
                    #df_t = pd.DataFrame(group)
                    #df_t = df_t.sort_values("week")
                    df_t2 = df_t.iloc[0:i]
                    avg_offense = df_t2[offense_column].mean()
                    avg_defense = df_t2[defense_column].mean()
                    offense_list.append(avg_offense)
                    defense_list.append(avg_defense)
            else:
                for i in range(num_of_games):
                    if i in [0,1,2]:
                        offense_list.append(np.nan) 
                        defense_list.append(np.nan)
                    else:
                        #df_t = pd.DataFrame(group)
                        #df_t = df_t.sort_values("week")
                        df_t2 = df_t.iloc[(i-qtrs):i]
                        avg_offense = df_t2[offense_column].mean()
                        avg_defense = df_t2[defense_column].mean()
                        offense_list.append(avg_offense)
                        defense_list.append(avg_defense)
                   
            df_t3 = (pd.DataFrame(group)
                  .sort_values("week")
                  .set_index("week")
                  .iloc[0:num_of_games]
                 )
            df_t3[f'avg_{offense_column}'] = offense_list
            df_t3[f'avg_{defense_column}'] = defense_list
            final_data = pd.concat([final_data, df_t3])
    
        final_data = final_data.reset_index().astype({"year": "int32", "week":"int32"})
        final_data = final_data[["team", "year", "week", f"avg_{offense_column}", f"avg_{defense_column}"]]
        final_data = pd.merge(final_data,home_away_table, how="left", left_on = ["week", "team", "year"], right_on = ["week", "team", "year"]).drop(columns = 'game_id')
        return final_data
    else:
        final_data = pd.DataFrame()
        groups = df.groupby(["team", "year"])
        for name, group in groups:
            diff_list = []
            df_t = pd.DataFrame(group)
            df_t = df_t.sort_values("week")
            num_of_games = df_t.shape[0]
            if qtrs == 'N':
                for i in range(num_of_games):
                    #df_t = pd.DataFrame(group)
                    #df_t = df_t.sort_values("week")
                    df_t2 = df_t.iloc[0:i]
                    avg_diff = df_t2[offense_column].mean()
                    diff_list.append(avg_diff)
            else:
                for i in range(num_of_games):
                    if i in [0,1,2]:
                        diff_list.append(np.nan)
                    else:
                        #df_t = pd.DataFrame(group)
                        #df_t = df_t.sort_values("week")
                        df_t2 = df_t.iloc[(i-qtrs):i]
                        avg_diff = df_t2[offense_column].mean()
                        diff_list.append(avg_diff)
                        
            df_t3 = (pd.DataFrame(group)
                  .sort_values("week")
                  .set_index("week")
                  .iloc[0:num_of_games]
                 )
            df_t3[f'avg_{offense_column}'] = diff_list
            final_data = pd.concat([final_data, df_t3])
            
        final_data = final_data.reset_index().astype({"year": "int32", "week":"int32"})
        final_data = final_data[["team", "year", "week", f"avg_{offense_column}"]]
        final_data = pd.merge(final_data,home_away_table, how="left", left_on = ["week", "team", "year"], right_on = ["week", "team", "year"]).drop(columns = 'game_id')
        return final_data        


### Creating a table in order to get the home/away attribute into each of the summary tables
def create_home_away_table(pbp_data):
    #Create table of home teams
    home_data = pbp_data.copy()[["game_id", "home_team", "year", "week"]]
    home_data["home_away"] = "home"
    home_data = home_data.copy().rename(columns = {"home_team": "team"})
    home_data = home_data.drop_duplicates()
    #Create table of away teams
    away_data = pbp_data.copy()[["game_id", "away_team", "year", "week"]]
    away_data["home_away"] = "away"
    away_data = away_data.copy().rename(columns = {"away_team": "team"})
    away_data = away_data.drop_duplicates()
    #Combine the tables
    home_away_data = pd.concat([home_data, away_data])
    home_away_data = home_away_data.astype({"year":"int32", "week":"int32"})
    home_away_data = home_away_data.drop_duplicates()
    return home_away_data

### Organize points scored and allowed by week/year/team ###
def points_scored_allowed(pbp_data):
    last_play = pbp_data["index"].isin(pbp_data[["index", "game_id"]].groupby("game_id").max()["index"].tolist())
    score_data = pbp_data[ last_play ] [["game_id", 'home_team', 'away_team', 'total_home_score', 'total_away_score', 'year', 'week']]
    home_data = score_data.copy()[["home_team", "year", "week", "total_home_score", "total_away_score"]]
    home_data = home_data.copy().rename(columns = {"home_team": "team", "total_home_score": "points_scored", "total_away_score": "points_allowed"})
    away_data = score_data.copy()[["away_team", "year", "week", "total_away_score", "total_home_score"]]
    away_data = away_data.copy().rename(columns = {"away_team": "team", "total_away_score": "points_scored", "total_home_score": "points_allowed"})
    score_data_final = pd.concat([home_data, away_data]).reset_index(drop=True)
    score_data_final = score_data_final.astype({"year": "int32","week": "int32", "points_scored": "int32", "points_allowed": "int32" })
    return score_data_final

### Yards gained and allowed by team/week/year ###
def yards_gained_allowed(pbp_data):
    yards_gained = (pbp_data[["game_id", "posteam",  "year", "week", "yards_gained"]]
     .groupby(["game_id", "posteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"posteam": "team"})   
    )
    yards_allowed = (pbp_data[["game_id", "defteam",  "year", "week", "yards_gained"]]
     .groupby(["game_id", "defteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"defteam": "team", "yards_gained": "yards_allowed"})   
    )
    yards_data_final = pd.merge(yards_gained, yards_allowed)
    return yards_data_final

### DF with performance against the spread (raw and capped) by team/year/week ###
def spread_diff_data(pbp_data):
    last_play = pbp_data["index"].isin(pbp_data[["index", "game_id"]].groupby("game_id").max()["index"].tolist())
    score_data = pbp_data[ last_play ].copy() [["game_id", 'home_team', 'away_team', 'total_home_score', 'total_away_score', 'spread_line', 'year', 'week']]
    home_data = score_data.copy()[["home_team", "year", "week", "total_home_score", "total_away_score", "spread_line"]]
    home_data['diff_from_spread'] = (home_data['total_home_score'] - home_data[ 'total_away_score']) - home_data['spread_line']
    home_data = home_data.copy().rename(columns = {"home_team": "team", "total_home_score": "points_scored", "total_away_score": "points_allowed"})
    away_data = score_data.copy()[["away_team", "year", "week", "total_away_score", "total_home_score", "spread_line"]]
    away_data['diff_from_spread'] = ((away_data.loc[:, 'total_home_score'] - away_data.loc[:, 'total_away_score']) - away_data.loc[:, 'spread_line']) * (-1)
    away_data = away_data.copy().rename(columns = {"away_team": "team", "total_away_score": "points_scored", "total_home_score": "points_allowed"})
    spread_diff_data_final = pd.concat([home_data, away_data]).reset_index(drop=True)
    spread_diff_data_final = (spread_diff_data_final
                              .astype({"year": "int32","week": "int32", "points_scored": "int32", "points_allowed": "int32" })
                                .drop(columns = ['points_scored', 'points_allowed'])
                            )
    spread_diff_data_final['diff_from_spread_capped'] = spread_diff_data_final['diff_from_spread'].clip(-10, 10) 
    return spread_diff_data_final

### Indicators for whether home and away team beat the spread in the prior week; at the game id level ###
def beat_spread_prior_wk(spread_data, pbp_data):
    spread_ind = spread_data.copy()
    spread_ind['spread_cover'] = np.where(spread_ind['diff_from_spread'] > 0, 'Y', 'N')
    spread_ind['next_week'] = spread_ind['week'] + 1
    spread_ind = spread_ind.drop(columns = ['spread_line', 'diff_from_spread_capped', 'week', 'diff_from_spread'])
    game_data = pbp_data[['game_id', 'home_team', 'away_team', 'year', 'week']].drop_duplicates()
    game_data = game_data.astype({'year':'int32', 'week':'int32'})
    spread_ind_for_mod = (pd.merge(game_data, spread_ind, how='left', left_on = ['home_team', 'year', 'week'], right_on = ['team', 'year', 'next_week'])
     .rename(columns = {'spread_cover': 'home_spread_cover_prior_wk'})
     .drop(columns = ['team', 'next_week'])
     .merge(spread_ind, how='left', left_on = ['away_team', 'year', 'week'], right_on = ['team', 'year', 'next_week'])
     .rename(columns = {'spread_cover': 'away_spread_cover_prior_wk'})
     .drop(columns = ['team', 'next_week', 'home_team', 'away_team', 'week', 'year'])
    )
    return spread_ind_for_mod

### Create DF with turnovers and turnovers forced at team/year/week level ###  
def turnover_data(pbp_data):
    turnover_data = pbp_data[["game_id", "home_team", "away_team", 'posteam', 'defteam', "fixed_drive", "fixed_drive_result", "year", "week"]]
    turnover_data = turnover_data[~turnover_data["posteam"].isna()]
    turnover_data = turnover_data.drop_duplicates()
    turnover_data["turnover_ind"] = np.where(turnover_data["fixed_drive_result"] == "Turnover", 1, 0)
    turnovers = (turnover_data[["game_id", "posteam",  "year", "week", "turnover_ind"]]
     .groupby(["game_id", "posteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"posteam": "team", "turnover_ind": "turnovers"})   
    )
    turnovers_forced = (turnover_data[["game_id", "defteam",  "year", "week", "turnover_ind"]]
     .groupby(["game_id", "defteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"defteam": "team", "turnover_ind": "turnovers_forced"})   
    )
    turnover_data_final = pd.merge(turnovers, turnovers_forced)
    return turnover_data_final

### QB hits forced and allowed by team/year/week ###
def qb_hits(pbp_data):
    qb_hit_data = pbp_data[["game_id", "home_team", "away_team", 'posteam', 'defteam', "qb_hit", "year", "week"]]
    qb_hits = (qb_hit_data[["game_id", "defteam",  "year", "week", "qb_hit"]]
     .groupby(["game_id", "defteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"defteam": "team", "qb_hit":"qb_hits"})   
    )
    qb_hits_allowed = (qb_hit_data[["game_id", "posteam",  "year", "week", "qb_hit"]]
     .groupby(["game_id", "posteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"posteam": "team", "qb_hit": "qb_hits_allowed"})
    )
    qb_hit_data_final = pd.merge(qb_hits, qb_hits_allowed)
    return qb_hit_data_final

### Helper function for two min data ###
def lead_change(x):
    try:
        if x.posteam == x.home_team:
            if x.total_home_score - x.total_away_score < 0:
                if x.post_drive_home_team_score - x.total_away_score >= 0:
                    return 1
        elif x.posteam == x.away_team:
            if x.total_away_score - x.total_home_score < 0:
                if x.post_drive_away_team_score - x.total_home_score >= 0:
                    return 1
        else:
            return 0
    except: 
        return 0

### Create DF with two min points scored and allowed at team/year/week level ###
def two_min_data(pbp_data):
    two_min_data = pbp_data[["game_id", "home_team", "away_team", 'posteam', 'defteam', 'half_seconds_remaining', "game_half", "total_home_score", "total_away_score", "fixed_drive", "fixed_drive_result", "year", "week"]]
    two_min_data = two_min_data.sort_values(["game_id", "fixed_drive", "half_seconds_remaining"], ascending = [True, True, False])
    two_min_data['drive_ordered'] = two_min_data.groupby(["game_id", "fixed_drive"]).cumcount() + 1
    two_min_data = two_min_data[ (two_min_data["drive_ordered"] == 1) & (two_min_data['half_seconds_remaining'] <= 180) ].copy()
    two_min_data['drive_points_scored'] = np.where(two_min_data["fixed_drive_result"] == 'Field goal', 3, np.where(two_min_data["fixed_drive_result"] == 'Touchdown', 7, 0) )
    two_min_data['post_drive_home_team_score'] = np.where(two_min_data["posteam"] == two_min_data["home_team"], two_min_data['total_home_score'] + two_min_data['drive_points_scored'], two_min_data['total_home_score'])
    two_min_data['post_drive_away_team_score'] = np.where(two_min_data["posteam"] == two_min_data["away_team"], two_min_data['total_away_score'] + two_min_data['drive_points_scored'], two_min_data['total_away_score'])
    two_min_data["posteam_takes_lead"] = two_min_data.apply(lead_change, axis = 1).fillna(0)
    two_min_data = two_min_data[two_min_data["drive_points_scored"] > 0].copy()
    two_min_data = two_min_data[(two_min_data["game_half"] == "Half1") | ( (two_min_data["game_half"] == "Half2") & (two_min_data["posteam_takes_lead"] == 1) )] 
    data_home = pbp_data[["game_id", "home_team", "year", "week"]]
    data_home = data_home.rename(columns = {"home_team": "team"})
    data_away = pbp_data[["game_id", "away_team", "year", "week"]]
    data_away = data_away.rename(columns = {"away_team": "team"})
    data_all = pd.concat([data_home, data_away]).drop_duplicates().reset_index(drop=True)
    two_min_scored = (two_min_data[["game_id", "posteam",  "year", "week", "drive_points_scored"]]
     .groupby(["game_id", "posteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"posteam": "team", "drive_points_scored": "two_min_scored"})   
    )
    two_min_scored = pd.merge(data_all, two_min_scored, how = "left")
    two_min_scored["two_min_scored"] = two_min_scored["two_min_scored"].fillna(0)

    two_min_allowed = (two_min_data[["game_id", "defteam",  "year", "week", "drive_points_scored"]]
     .groupby(["game_id", "defteam",  "year", "week"])
     .sum()
    .reset_index()
    .rename(columns = {"defteam": "team", "drive_points_scored": "two_min_allowed"})   
    )
    two_min_allowed = pd.merge(data_all, two_min_allowed, how = 'left')
    two_min_allowed["two_min_allowed"] = two_min_allowed["two_min_allowed"].fillna(0)
    two_min_data_final = pd.merge(two_min_scored, two_min_allowed)
    return two_min_data_final

### Create indicators for whether the home and/or away team has their non-week 1 starter at QB ###
def backup_qb_data(pbp_data, home_away_data): 
    passer_data_home = pbp_data[['game_id', 'home_team', 'away_team', 'posteam', 'passer_player_name', 'year', 'week']] [(pbp_data['home_team']==pbp_data['posteam']) & (pbp_data['passer_player_name'].notna())]
    passer_data_home = passer_data_home.reset_index()
    passer_data_home =passer_data_home [passer_data_home["index"].isin(passer_data_home[["index", "game_id"]].groupby("game_id").min()["index"].tolist()) ]
    passer_data_home = passer_data_home.drop(columns = ['away_team', 'posteam', 'index']).rename(columns = {'home_team': 'team', 'passer_player_name': 'starting_qb'})                       
    
    passer_data_away = pbp_data[['game_id', 'home_team', 'away_team', 'posteam', 'passer_player_name', 'year', 'week']] [(pbp_data['away_team']==pbp_data['posteam']) & (pbp_data['passer_player_name'].notna())]
    passer_data_away = passer_data_away.reset_index()
    passer_data_away =passer_data_away [passer_data_away["index"].isin(passer_data_away[["index", "game_id"]].groupby("game_id").min()["index"].tolist()) ]
    passer_data_away = passer_data_away.drop(columns = ['home_team', 'posteam', 'index']).rename(columns = {'away_team': 'team', 'passer_player_name': 'starting_qb'}) 

    passer_data = pd.concat([passer_data_home, passer_data_away])
    week_1_starter = passer_data[passer_data['week'] == 1].drop(columns = ['week', 'game_id']).rename(columns = {'starting_qb': 'week_1_starter'})
    manual_fix = pd.DataFrame({'team': ['TB', 'MIA'], 'week_1_starter': ['J.Winston', 'J.Cutler'], 'year':[2017, 2017]})
    week_1_starter = pd.concat([week_1_starter, manual_fix])
    backup_data = pd.merge(passer_data, week_1_starter, left_on = ['team', 'year'], right_on = ['team', 'year'])
    backup_data['indicator'] = np.where(backup_data['starting_qb'] == backup_data['week_1_starter'], 'N', 'Y')
    backup_data = backup_data[['game_id', 'team', 'indicator']]

    backup_data[['year', 'week']] = backup_data['game_id'].str.split("_", expand=True)[[0,1]]
    backup_data = backup_data.astype({'year': 'int32', 'week':'int32'})

    backup_data = pd.merge(backup_data, home_away_data.drop(columns = 'game_id'), how='left', on = ['team', 'week', 'year'])

    backup_data_home = (backup_data[backup_data['home_away'] == 'home'].
                    rename(columns = {'indicator': 'qb_backup_home'}).
                    drop(columns = ['team', 'week', 'year', 'home_away'])
                   )

    backup_data_away = (backup_data[backup_data['home_away'] == 'away'].
                    rename(columns = {'indicator': 'qb_backup_away'}).
                    drop(columns = ['team', 'week', 'year', 'home_away'])
                   )

    backup_data_for_mod = pd.merge(backup_data_home, backup_data_away, how= 'left', on = 'game_id')
    return backup_data_for_mod

### Create table with DVOA rank and weighted DVOA for the home and away teams ###
def DVOA_data(pbp_data, home_away_data):
    home_away_data_temp = home_away_data.copy()
    home_away_data_temp[['new_home', 'new_away']] = home_away_data_temp['game_id'].str.split("_", expand=True)[[3,2]]
    home_away_data_temp['team'] = np.where(home_away_data_temp['home_away']=='home', home_away_data_temp['new_home'], home_away_data_temp['new_away'])
    home_away_data_temp = home_away_data_temp.drop(columns = ['new_home', 'new_away'])
    year_list = ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022']
    DVOA = pd.DataFrame()
    for year in year_list:
        if year in ['2021', '2022']:
            wks = 18
        else:
            wks = 17
        for week in range(wks):
            week = week + 1
            df_temp = pd.read_csv(f"DVOA/{year} Team DVOA Ratings, Overall after Week {week}.csv")
            df_temp['week'] = week + 1
            df_temp['year'] = year
            df_temp = df_temp[df_temp['week'] <= 17]
            df_temp = df_temp.astype({'year': 'int32'})
            df_temp = df_temp.rename(columns = {'Team':'team'})
            DVOA = pd.concat([DVOA, df_temp])
         
    DVOA = pd.merge(DVOA, home_away_data_temp, how = 'left', left_on = ['team', 'year', 'week'], right_on = ['team', 'year', 'week'])
    DVOA = DVOA[['team','year', 'week', 'Weighted DVOA', 'Total DVOA Rank', 'home_away']]
    DVOA['Weighted DVOA'] = DVOA.apply(lambda x: x["Weighted DVOA"].strip('%'), axis = 1).astype('float64') / 100
    games = pd.DataFrame(pbp_data['game_id']).drop_duplicates()
    games[["year", "week"]]= games['game_id'].str.split("_", expand=True)[[0,1]]
    games[["home_team", "away_team"]] = games['game_id'].str.split("_", expand=True)[[3,2]]
    games = games.astype({'year': 'int32', 'week':'int64'})

    DVOA_home = (DVOA[DVOA['home_away'] == 'home']
             .merge(games[['game_id', 'home_team', 'year', 'week']], left_on = ['team', 'year', 'week'], right_on = ['home_team', 'year', 'week'])
            .rename(columns = {"Weighted DVOA": 'weighted_dvoa_home', 'Total DVOA Rank': 'total_dvoa_rank_home'})
             .drop(columns = ['team','year', 'week', 'home_away', 'home_team'])
            )
    DVOA_away = (DVOA[DVOA['home_away'] == 'away']
             .merge(games[['game_id', 'away_team', 'year', 'week']], left_on = ['team', 'year', 'week'], right_on = ['away_team', 'year', 'week'])
            .rename(columns = {"Weighted DVOA": 'weighted_dvoa_away', 'Total DVOA Rank': 'total_dvoa_rank_away'})
             .drop(columns = ['team', 'year', 'week', 'home_away', 'away_team'])
            )
    DVOA_for_mod = pd.merge(DVOA_home, DVOA_away, left_on = 'game_id', right_on='game_id')
    DVOA_for_mod = DVOA_for_mod[['game_id', 'weighted_dvoa_home', 'total_dvoa_rank_home', 'weighted_dvoa_away', 'total_dvoa_rank_away']]
    return DVOA_for_mod

### Derive several game level attributes for modeling/analysis: temp at kickoff, spread line, total line, whether
### the home team covered the spread, actual spread line, difference between actual spread line and final spread line 
def game_attributes(pbp_data):
    last_play_index = pbp_data["index"].isin(pbp_data[["index", "game_id"]].groupby("game_id").max()["index"].tolist())
    final_score = pbp_data[ last_play_index ] [["game_id",  'total_home_score', 'total_away_score',  "spread_line"]]
    final_score["home_spread_cover"] = np.where(final_score["total_home_score"] - final_score["total_away_score"] - final_score["spread_line"] == 0, 'NA',final_score["total_home_score"] - final_score["total_away_score"] - final_score["spread_line"] > 0) 
    final_score['spread_final'] = final_score['total_home_score'] - final_score['total_away_score']
    final_score['spread_diff'] = final_score['spread_final'] - final_score['spread_line']
    spread_cover_final = final_score.drop(columns = ["total_home_score", "total_away_score", "spread_line"])
    game_att = pbp_data[["game_id", "home_team", "away_team", "temperature", "start_time", "spread_line", "total_line"]].drop_duplicates()
    game_att["temperature"] = np.where(game_att["temperature"].isna(), 70, game_att["temperature"])
    game_att[["year", "week"]] = pbp_data["game_id"].str.split("_", expand=True)[[0,1]] 
    game_att = game_att.astype({"week":'int32', "year":'int32'})
    game_att = pd.merge(game_att, spread_cover_final, how="left", left_on = "game_id", right_on = "game_id")
    game_att = game_att[game_att["home_spread_cover"] != 'NA']
    return game_att

### Calculate the distance traveled by the away team ###
def distanced_traveled(pbp_data):
    lat_lng_cities = pd.read_csv("uscities.csv")
    city_mapping = pd.read_csv("city mapping.csv")
    lat_lng_cities_trunc = lat_lng_cities[["city", "state_id", "lat", "lng"]]
    city_locations = pd.merge(city_mapping, lat_lng_cities_trunc, left_on = ["City", "State"], right_on = ["city", "state_id"], how = "left")
    city_loc_trunc = city_locations.copy()[["Abbreviation", "lat", "lng"]]
    city_loc_trunc["Abbreviation"] = city_loc_trunc["Abbreviation"].str.strip()
    distance_data = pd.DataFrame(pbp_data["game_id"].drop_duplicates())
    distance_data[['home_team', 'away_team']] = distance_data['game_id'].str.split("_", expand = True)[[3, 2]]
    distance_data = pd.merge(distance_data, city_loc_trunc, left_on = "home_team", right_on="Abbreviation", how = "left")
    distance_data = distance_data.rename(columns = {"lat": "home_lat", "lng": "home_lng"})
    distance_data = pd.merge(distance_data, city_loc_trunc, left_on = "away_team", right_on="Abbreviation", how = "left")
    distance_data = distance_data.rename(columns = {"lat": "away_lat", "lng": "away_lng"})
    distance_data = distance_data.drop(columns = ["Abbreviation_x", "Abbreviation_y"])
    distance_data["distance_traveled"] = distance_data.apply(lambda x: haversine((x.home_lat, x.home_lng), (x.away_lat, x.away_lng), unit = 'mi'), axis =1 )
    distance_data = distance_data.drop(columns = ["home_lat", "home_lng", "away_lat", "away_lng"])
    return distance_data

### Finalize the modeling dataset: bring together individual tables, bin some continuous variables, derive difference features ### 
def finalize_modeling_dataset(game_att, scored_data_for_mod, yards_data_for_mod, turnover_data_for_mod,
    qb_hit_data_for_mod, two_min_data_for_mod, scored_momen_data_for_mod, spread_diff_capped_data_for_mod,
    spread_diff_momen_capped_data_for_mod, DVOA_for_mod, distance_data, backup_data_for_mod, spread_ind_for_mod):
    game_attr = (pd.merge(game_att, distance_data, how="left", left_on = ["game_id", "home_team", "away_team"], right_on = ["game_id", "home_team", "away_team"] )
                .merge(backup_data_for_mod, how="left", on = 'game_id')
             .merge(spread_ind_for_mod, how="left", on = 'game_id')
    )
    data_merged = (pd.merge(scored_data_for_mod, yards_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"])
     .merge(turnover_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"] )
     .merge(qb_hit_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"] )
    .merge(two_min_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"] )
    .merge(scored_momen_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"] )
    .merge(spread_diff_capped_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"])
    .merge(spread_diff_momen_capped_data_for_mod, how = "left", left_on = ["week", "team", "year", "home_away"], right_on = ["week", "team", "year", "home_away"])
    )   
    data_merged_home = data_merged[data_merged["home_away"] == "home"]
    data_merged_home = data_merged_home.rename(columns = {"avg_points_scored": "avg_points_scored_home" , "avg_points_allowed": "avg_points_allowed_home" , "avg_yards_gained": "avg_yards_gained_home" , "avg_yards_allowed": "avg_yards_allowed_home" , "avg_turnovers": "avg_turnovers_home" , "avg_turnovers_forced": "avg_turnovers_forced_home" , "avg_qb_hits_allowed": "avg_qb_hits_allowed_home" , "avg_qb_hits": "avg_qb_hits_home" , "avg_two_min_scored": "avg_two_min_scored_home" , "avg_two_min_allowed": "avg_two_min_allowed_home", 'avg_points_scored_momen': 'avg_points_scored_momen_home', 'avg_points_allowed_momen': 'avg_points_allowed_momen_home', 'avg_diff_from_spread_capped': 'avg_diff_from_spread_capped_home', 'avg_diff_from_spread_3q': 'avg_diff_from_spread_3q_home'}  ).drop(columns = ["home_away"])
    data_merged_away = data_merged[data_merged["home_away"] == "away"]
    data_merged_away = data_merged_away.rename(columns = {"avg_points_scored": "avg_points_scored_away" , "avg_points_allowed": "avg_points_allowed_away" , "avg_yards_gained": "avg_yards_gained_away" , "avg_yards_allowed": "avg_yards_allowed_away" , "avg_turnovers": "avg_turnovers_away" , "avg_turnovers_forced": "avg_turnovers_forced_away" , "avg_qb_hits_allowed": "avg_qb_hits_allowed_away" , "avg_qb_hits": "avg_qb_hits_away" , "avg_two_min_scored": "avg_two_min_scored_away" , "avg_two_min_allowed": "avg_two_min_allowed_away", 'avg_points_scored_momen': 'avg_points_scored_momen_away', 'avg_points_allowed_momen': 'avg_points_allowed_momen_away','avg_diff_from_spread_capped': 'avg_diff_from_spread_capped_away', 'avg_diff_from_spread_3q': 'avg_diff_from_spread_3q_away'}  ).drop(columns = ["home_away"])
    modeling_dataset = (pd.merge(game_attr, data_merged_home, how="left", left_on = ["year", "week", "home_team"], right_on = ["year", "week","team" ])
     .drop(columns = ["team"])           
    .merge(data_merged_away, how="left", left_on = ["year", "week", "away_team"], right_on = ["year", "week","team" ])
    .drop(columns = ["team"])
    )
    modeling_dataset['prime_time'] = np.where(modeling_dataset['start_time'] >'20:00:00', 'prime_time', 'not_prime_time' )
    modeling_dataset['temp_cat'] = np.where(modeling_dataset['temperature'] < 30, 'cold',  'normal')
    modeling_dataset['distance_bucket'] = np.where(modeling_dataset['distance_traveled'] > 1800, 'Extreme Distance', 'Not Extreme Distance')
    modeling_dataset = pd.merge(modeling_dataset, DVOA_for_mod, how="left", on = 'game_id')
    modeling_dataset['avg_points_scored_diff'] = modeling_dataset['avg_points_scored_home'] - modeling_dataset['avg_points_scored_away']
    modeling_dataset['avg_points_allowed_diff'] = modeling_dataset['avg_points_allowed_home'] - modeling_dataset['avg_points_allowed_away']

    modeling_dataset['avg_yards_gained_diff'] = modeling_dataset['avg_yards_gained_home'] - modeling_dataset['avg_yards_gained_away']
    modeling_dataset['avg_yards_allowed_diff'] = modeling_dataset['avg_yards_allowed_home'] - modeling_dataset['avg_yards_allowed_away']

    modeling_dataset['avg_turnovers_diff'] = modeling_dataset['avg_turnovers_home'] - modeling_dataset['avg_turnovers_away']
    modeling_dataset['avg_turnovers_forced_diff'] = modeling_dataset['avg_turnovers_forced_home'] - modeling_dataset['avg_turnovers_forced_away']

    modeling_dataset['avg_point_differential_home'] = (modeling_dataset['avg_points_scored_home'] - modeling_dataset['avg_points_allowed_home']).fillna(0)
    modeling_dataset['avg_point_differential_away'] = (modeling_dataset['avg_points_scored_away'] - modeling_dataset['avg_points_allowed_away']).fillna(0)

    modeling_dataset['avg_point_differential_diff'] = modeling_dataset['avg_point_differential_home'] - modeling_dataset['avg_point_differential_away']
    modeling_dataset['avg_yard_differential_diff'] =( modeling_dataset['avg_yards_gained_home'] - modeling_dataset['avg_yards_allowed_home'] ) - (modeling_dataset['avg_yards_gained_away'] - modeling_dataset['avg_yards_allowed_away'])
    modeling_dataset['avg_turnover_differential_diff'] = modeling_dataset['avg_turnovers_forced_diff'] - modeling_dataset['avg_turnovers_diff']

    modeling_dataset['weighted_dvoa_diff'] = modeling_dataset['weighted_dvoa_home'].fillna(0) - modeling_dataset['weighted_dvoa_away'].fillna(0)
    modeling_dataset['total_dvoa_rank_diff'] = modeling_dataset['total_dvoa_rank_home'].fillna(0) - modeling_dataset['total_dvoa_rank_away'].fillna(0)

    modeling_dataset['avg_diff_from_spread_capped_diff'] = modeling_dataset['avg_diff_from_spread_capped_home'].fillna(0) - modeling_dataset['avg_diff_from_spread_capped_away'].fillna(0)
    modeling_dataset['avg_diff_from_spread_capped_3q'] = modeling_dataset['avg_diff_from_spread_3q_home'].fillna(0) - modeling_dataset['avg_diff_from_spread_3q_away'].fillna(0)

    modeling_dataset['avg_point_momen_differential_home'] = modeling_dataset['avg_points_scored_momen_home'].fillna(0) - modeling_dataset['avg_points_allowed_momen_home'].fillna(0)
    modeling_dataset['avg_point_momen_differential_away'] = modeling_dataset['avg_points_scored_momen_away'].fillna(0) - modeling_dataset['avg_points_allowed_momen_away'].fillna(0)
    modeling_dataset['avg_point_momen_differential_diff'] = modeling_dataset['avg_point_momen_differential_home'].fillna(0) - modeling_dataset['avg_point_momen_differential_away'].fillna(0)

    modeling_dataset['avg_qb_hits_differential_diff'] = (modeling_dataset['avg_qb_hits_home'] - modeling_dataset['avg_qb_hits_allowed_home']) - (modeling_dataset['avg_qb_hits_away'] - modeling_dataset['avg_qb_hits_allowed_away'])

    modeling_dataset['avg_two_min_differential_diff'] = (modeling_dataset['avg_two_min_scored_home'] - modeling_dataset['avg_two_min_allowed_home']) - (modeling_dataset['avg_two_min_scored_away'] - modeling_dataset['avg_two_min_allowed_away'])
    return modeling_dataset