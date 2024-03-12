mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
[theme]\n\
base=\"light\"
\n\
" > ~/.streamlit/config.toml
