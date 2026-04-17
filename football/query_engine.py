import re
from thefuzz import process, fuzz
import pandas as pd

# Define intent categories with regex patterns (Simple NLP Bag-of-Words approach)
INTENT_PATTERNS = {
    "top_players": [r"\btop\b", r"\bbest\b", r"most goals", r"top scorer", r"highest"],
    "compare_players": [r"compare", r"better", r"versus", r"\bvs\b"],
    "player_stats": [r"\bstats\b", r"performance", r"how did.*play", r"goals for", r"how many goals", r"how many assists"],
    "trend_chart": [r"trend", r"history", r"progress", r"over time"]
}

def _extract_entities(query, player_list, score_cutoff=85, max_entities=2):
    """Finds up to max_entities best player name matches in a query string."""
    if not player_list:
        return []

    # extract using token_set_ratio to handle partial name matches regardless of word order
    matches = process.extract(query, player_list, scorer=fuzz.token_set_ratio, limit=5)
    
    entities = []
    for match, score in matches:
        if score >= score_cutoff:
            if match not in entities:
                entities.append(match)
        if len(entities) == max_entities:
            break
            
    # Fallback to partial_ratio if token_set_ratio is too strict
    if not entities:
        best = process.extractOne(query, player_list, scorer=fuzz.partial_ratio)
        if best and best[1] >= score_cutoff:
            entities.append(best[0])
            
    return entities

def parse_query(query, df, player_list=[]):
    """Parses a query to find intent and computes the answer from df."""
    if not query:
        return {"intent": "unknown", "entities": [], "message": None}
        
    query_lower = query.lower()
    
    # 1. Extract player name entities first
    entities = _extract_entities(query, player_list)
    
    # 2. Determine intent from the query
    intent = "unknown"
    for intnt, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                intent = intnt
                break
        if intent != "unknown":
            break

    # 3. If no intent keyword is found but player(s) were, assume intent
    if intent == "unknown" and entities:
        if len(entities) > 1:
            intent = "compare_players"
        else:
            intent = "player_stats"

    player_col = "player"
    goals_col = "gls"
    assists_col = "ast"
    
    message = None
    
    # 4. Compute Data Answer
    if df.empty:
        message = "No data available to answer the query."
        return {"intent": intent, "entities": entities, "message": message}

    if intent == "top_players":
        if player_col in df.columns and goals_col in df.columns:
            top = df.groupby(player_col)[goals_col].sum().sort_values(ascending=False).head(1)
            if not top.empty:
                top_player = top.index[0]
                top_goals = int(top.iloc[0])
                message = f"🏆 **{top_player}** is the top scorer with **{top_goals} goals**."
                entities = [top_player] # Sync UI to top player
            
    elif intent == "compare_players":
        if len(entities) >= 2:
            p1, p2 = entities[0], entities[1]
            p1_stats = df[df[player_col] == p1][[goals_col, assists_col]].sum()
            p2_stats = df[df[player_col] == p2][[goals_col, assists_col]].sum()
            
            p1_goals, p1_ast = int(p1_stats[goals_col]), int(p1_stats[assists_col])
            p2_goals, p2_ast = int(p2_stats[goals_col]), int(p2_stats[assists_col])
            
            message = f"🔥 **{p1}** ({p1_goals}G, {p1_ast}A) vs **{p2}** ({p2_goals}G, {p2_ast}A)."
        elif len(entities) == 1:
            message = f"I found **{entities[0]}**. Please specify a second player to compare."
            
    elif intent == "player_stats":
        if entities:
            p1 = entities[0]
            p1_stats = df[df[player_col] == p1][[goals_col, assists_col]].sum()
            p1_goals, p1_ast = int(p1_stats[goals_col]), int(p1_stats[assists_col])
            
            # matches played col
            mp_col = "mp" if "mp" in df.columns else "age" # age is just a fallback to check logic
            
            if "mp" in df.columns:
                matches = df[df[player_col] == p1]["mp"].sum()
                message = f"✅ **{p1}** has scored **{p1_goals} goals** and provided **{p1_ast} assists** in {int(matches)} matches."
            else:
                message = f"✅ **{p1}** has scored **{p1_goals} goals** and provided **{p1_ast} assists**."
    
    elif intent == "trend_chart":
        if entities:
            message = f"📈 Showing trend chart for **{entities[0]}**."
            
    # Default message if nothing matched or computed
    if not message:
        if entities:
            message = f"✅ Showing data for **{entities[0]}**."
        else:
            message = "I didn't understand that. Try asking 'who is the top scorer?' or 'stats for Bukayo Saka'."

    return {"intent": intent, "entities": entities, "message": message}