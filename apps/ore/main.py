import fastapi
import uvicorn
from scraper import pdf_scraper, realtime

app = fastapi.FastAPI()

@app.get("/download-pdfs")
def parse():
    pdf_scraper.main()
    return {"message": "PDFs downloaded successfully."}

@app.get("/realtime-scrape")
def realtime_scrape():
    if hasattr(realtime, "main"):
        realtime.main()
    return {"message": "Real-time scraping completed successfully."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
