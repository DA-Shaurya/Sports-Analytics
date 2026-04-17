import panel as pn
import pandas as pd
import hvplot.pandas
import panel.template as pnt
from data_loader import load_data
from query_engine import parse_query

pn.extension('tabulator', theme="dark")


def create_dashboard():
    import os
    
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    css_path = os.path.join(os.path.dirname(__file__), "custom_style.css")
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_template = f.read()
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
        
    # Inject CSS into the postamble block
    if "{% block postamble %}" in html_template:
        html_template = html_template.replace("{% block postamble %}", f"{{% block postamble %}}\n<style>\n{css_content}\n</style>")
    else:
        # Fallback if block is not found
        pass
    df = load_data()

    # -------------------------------
    # CLEAN DATA
    # -------------------------------

    player_col = "player"
    goals_col = "gls"
    assists_col = "ast"
    team_col = "squad"
    pos_col = "pos"
    league_col = "comp"

    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()
        for col in [goals_col, assists_col]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                df[col] = 0

    all_players = df[player_col].dropna().unique().tolist() if not df.empty and player_col in df.columns else []

    # -------------------------------
    # FILTERS
    # -------------------------------
    teams = sorted(df[team_col].dropna().unique()) if not df.empty and team_col in df.columns else []
    positions = sorted(df[pos_col].dropna().unique()) if not df.empty and pos_col in df.columns else []
    leagues = sorted(df[league_col].dropna().unique()) if not df.empty and league_col in df.columns else []
    
    team_filter = pn.widgets.Select(name="Team", options=["All"] + teams)
    pos_filter = pn.widgets.Select(name="Position", options=["All"] + positions)
    league_filter = pn.widgets.Select(name="League", options=["All"] + leagues)

    # -------------------------------
    # QUERY
    # -------------------------------
    query_input = pn.widgets.TextInput(name="Ask a question", placeholder="e.g., stats for Brenden Aaronson")

    def apply_filters(data):
        if data.empty:
            return data
        if team_filter.value != "All":
            data = data[data[team_col] == team_filter.value]
        if pos_filter.value != "All":
            data = data[data[pos_col] == pos_filter.value]
        if league_filter.value != "All":
            data = data[data[league_col] == league_filter.value]
        return data

    def get_players():
        if df.empty or player_col not in df.columns:
            return ["None"]
        players = sorted(apply_filters(df)[player_col].dropna().unique().tolist())
        return players if players else ["None"]

    # -------------------------------
    # PLAYER SELECTORS
    # -------------------------------
    player_select = pn.widgets.Select(name="Select Player", options=get_players())
    player_compare_1 = pn.widgets.Select(name="Player 1", options=get_players())
    player_compare_2 = pn.widgets.Select(name="Player 2", options=get_players())

    @pn.depends(team_filter, pos_filter, league_filter, watch=True)
    def update_players(*_):
        players = get_players()
        player_select.options = players
        player_compare_1.options = players
        player_compare_2.options = players
        
        if players:
            player_select.value = players[0]
            player_compare_1.value = players[0]
            player_compare_2.value = players[0]

    # -------------------------------
    # PLAYER PERFORMANCE
    # -------------------------------
    @pn.depends(player_select, team_filter, pos_filter, league_filter)
    def player_stats(player, *_):
        data = apply_filters(df)
        if player == "None" or data.empty or player_col not in data.columns:
            return pn.pane.Markdown("No data available.")
            
        stats = data[data[player_col] == player][[goals_col, assists_col]].sum()

        return stats.hvplot.bar(
            title=f"{player} Performance",
            height=300,
            responsive=True,
            color='#10b981' # Vibrant green
        ).opts(
            toolbar=None,
            bgcolor='rgba(0,0,0,0)',
            show_grid=True,
            gridstyle={'color': '#374151', 'line_dash': 'dashed'},
            xaxis='bottom',
            fontscale=1.1,
            yformatter='%d',
            shared_axes=False
        )

    # -------------------------------
    # TREND
    # -------------------------------
    @pn.depends(player_select, team_filter, pos_filter, league_filter)
    def trend_chart(player, *_):
        data = apply_filters(df)
        if player == "None" or data.empty or player_col not in data.columns:
            return pn.pane.Markdown("No data available.")
            
        stats = data[data[player_col] == player][[goals_col, assists_col]].sum()

        return stats.hvplot.barh(
            title=f"{player} Profile",
            height=300,
            responsive=True,
            color='#3b82f6' # Vibrant blue
        ).opts(
            toolbar=None,
            bgcolor='rgba(0,0,0,0)',
            show_grid=True,
            gridstyle={'color': '#374151', 'line_dash': 'dashed'},
            fontscale=1.1,
            xformatter='%d',
            shared_axes=False
        )

    # -------------------------------
    # COMPARISON
    # -------------------------------
    @pn.depends(player_compare_1, player_compare_2, team_filter, pos_filter, league_filter)
    def compare_players(p1, p2, *_):
        data = apply_filters(df)
        if "None" in (p1, p2) or data.empty or player_col not in data.columns:
            return pn.pane.Markdown("No data available to compare.")

        df1 = data[data[player_col] == p1]
        df2 = data[data[player_col] == p2]

        stats1 = df1[[goals_col, assists_col]].sum()
        stats2 = df2[[goals_col, assists_col]].sum()

        compare_df = pd.DataFrame({
            "Player": [p1, p2],
            "Goals": [stats1[goals_col], stats2[goals_col]],
            "Assists": [stats1[assists_col], stats2[assists_col]]
        })

        compare_df = compare_df.melt(
            id_vars="Player",
            var_name="Metric",
            value_name="Value"
        )

        return compare_df.hvplot.bar(
            x="Metric",
            y="Value",
            by="Player",
            title="🔥 Player Comparison",
            height=350,
            responsive=True,
            cmap=['#ec4899', '#8b5cf6'] # Pink and Purple
        ).opts(
            toolbar=None,
            bgcolor='rgba(0,0,0,0)',
            show_grid=True,
            gridstyle={'color': '#374151', 'line_dash': 'dashed'},
            fontscale=1.1,
            yformatter='%d',
            legend_position='top_right',
            shared_axes=False
        )

    # -------------------------------
    # TOP PLAYERS
    # -------------------------------
    @pn.depends(team_filter, pos_filter, league_filter)
    def top_players(*_):
        data = apply_filters(df)
        if data.empty or player_col not in data.columns:
            return pn.pane.Markdown("No data available.")
            
        top = data.groupby(player_col)[[goals_col, assists_col]].sum()
        top["total"] = top[goals_col] + top[assists_col]
        top = top.sort_values("total", ascending=False).head(10)

        return top.hvplot.bar(
            y="total",
            title="🏆 Top Players",
            height=350,
            responsive=True,
            hover_cols=[goals_col, assists_col],
            color='#f59e0b' # Vibrant amber/gold
        ).opts(
            toolbar='above', # Enable interactive toolbar for zooming/panning
            default_tools=['hover', 'pan', 'wheel_zoom', 'reset'],
            bgcolor='rgba(0,0,0,0)',
            show_grid=True,
            gridstyle={'color': '#374151', 'line_dash': 'dashed'},
            xrotation=45,
            fontscale=1.1,
            yformatter='%d',
            shared_axes=False
        )

    @pn.depends(query_input)
    def query_output(q):
        if not q:
            return pn.pane.Markdown("Try: 'top scorers' or 'compare Bukayo Saka and Phil Foden'", styles={'color': '#9ca3af'})
            
        filtered_data = apply_filters(df)
        result = parse_query(q, filtered_data, all_players)
        entities = result.get("entities", [])
        message = result.get("message", "")

        # --- Sync UI Automatically ---
        if entities:
            # Sync first entity
            e1 = entities[0]
            if e1 in player_select.options:
                player_select.value = e1
            
            # Sync second entity for comparison
            if len(entities) > 1:
                e2 = entities[1]
                if e1 in player_compare_1.options:
                    player_compare_1.value = e1
                if e2 in player_compare_2.options:
                    player_compare_2.value = e2

        return pn.pane.Markdown(message, styles={'color': '#10b981'})

    @pn.depends(team_filter, pos_filter, league_filter)
    def filtered_data_table(*_):
        filtered_df = apply_filters(df)
        if filtered_df.empty:
            return pn.pane.Markdown("### No data to display for the current selection.")
        
        display_cols = {
            player_col: "Player", team_col: "Team", league_col: "League",
            pos_col: "Position", goals_col: "Goals", assists_col: "Assists",
            "age": "Age", "mp": "Matches Played", "min": "Minutes"
        }
        
        existing_cols = {k: v for k, v in display_cols.items() if k in filtered_df.columns}
        table_df = filtered_df[list(existing_cols.keys())].rename(columns=existing_cols)
        
        return pn.widgets.Tabulator(
            table_df, layout='fit_data_table', page_size=15, theme='modern',
            disabled=True, sizing_mode="stretch_width"
        )

    # -------------------------------
    # LAYOUT
    # -------------------------------
    # Group filters into a clean, collapsible native Accordion
    filters_accordion = pn.Accordion(
        ('Advanced Filters', pn.Column(team_filter, pos_filter, league_filter)),
        active=[0], # Open by default
        sizing_mode='stretch_width'
    )
    
    template = pn.Template(html_template)
    
    template.add_panel('filters_accordion', filters_accordion)
    template.add_panel('query_input', query_input)
    template.add_panel('query_output', query_output)
    
    template.add_panel('player_select', player_select)
    template.add_panel('player_stats', player_stats)
    template.add_panel('trend_chart', trend_chart)
    
    template.add_panel('player_compare_1', player_compare_1)
    template.add_panel('player_compare_2', player_compare_2)
    template.add_panel('compare_players', compare_players)
    
    template.add_panel('top_players', top_players)
    template.add_panel('filtered_data_table', filtered_data_table)
    
    return template