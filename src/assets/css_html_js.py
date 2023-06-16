custom_css = """
#changelog-text {
    font-size: 16px !important;
}

#changelog-text h2 {
    font-size: 18px !important;
}

.markdown-text {
    font-size: 16px !important;
}

#models-to-add-text {
    font-size: 18px !important;
}

#citation-button span {
    font-size: 16px !important;
}

#citation-button textarea {
    font-size: 16px !important;
}

#citation-button > label > button {
    margin: 6px;
    transform: scale(1.3);
}

#leaderboard-table {
    margin-top: 15px
}

#leaderboard-table-lite {
    margin-top: 15px
}

#search-bar-table-box > div:first-child {
    background: none;
    border: none;
}
 
#search-bar {
    padding: 0px;
    width: 30%;
}

/* Hides the final AutoEvalColumn */
#llm-benchmark-tab-table table td:last-child,
#llm-benchmark-tab-table table th:last-child {
    display: none;
}

/* Limit the width of the first AutoEvalColumn so that names don't expand too much */
table td:first-child,
table th:first-child {
    max-width: 400px;
    overflow: auto;
    white-space: nowrap;
}

.tab-buttons button {
    font-size: 20px;
}

#scale-logo {
    border-style: none !important;
    box-shadow: none;
    display: block;
    margin-left: auto;
    margin-right: auto;
    max-width: 600px;
}

#scale-logo .download {
    display: none;
}
"""

get_window_url_params = """
    function(url_params) {
        const params = new URLSearchParams(window.location.search);
        url_params = Object.fromEntries(params);
        return url_params;
    }
    """
