from config import Settings

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='app:app', host=Settings.Api["HOST"], port=Settings.Api["PORT"], reload=Settings.Api["RELOAD"])