import hvplot.pandas

def top_players_chart(df, player_col="player", goals_col="gls"):
    if df.empty or player_col not in df.columns or goals_col not in df.columns:
        return "No data available."
        
    top = df.groupby(player_col)[goals_col].sum().reset_index()
    top = top.sort_values(by=goals_col, ascending=False).head(10)

    return top.hvplot.bar(
        x=player_col,
        y=goals_col,
        title="Top Goal Scorers",
        height=400,
        width=700,
        responsive=True
    ).opts(toolbar=None)