from website import create_app

app = create_app()

if __name__ == '__main__':  # main can't be imported, it can only be run
    app.run(debug=True)  # on change rerun the server
