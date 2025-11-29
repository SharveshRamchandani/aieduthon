from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import slides, notes, quizzes, export, orchestrate, generate


def create_app() -> FastAPI:
	app = FastAPI(title="AI Presentation Service", version="0.1.0")

	# CORS for local dev (frontend on Vite default 5173)
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.include_router(slides.router, prefix="/slides", tags=["slides"])
	app.include_router(notes.router, prefix="/slides", tags=["speaker-notes"])
	app.include_router(quizzes.router, prefix="/slides", tags=["quizzes"])
	app.include_router(export.router, prefix="/slides", tags=["export"])
	app.include_router(orchestrate.router, tags=["orchestrate"])
	app.include_router(generate.router, tags=["generate"])

	# Serve generated images as static files so the frontend can display them
	app.mount(
		"/media",
		StaticFiles(directory="out/generated_images"),
		name="media",
	)

	return app


app = create_app()


