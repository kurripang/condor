//! Biblioteca principal de Cóndor.

use serde::{Deserialize, Serialize};
use std::path::Path;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum OASFError {
    #[error("Archivo no encontrado: {0}")]
    FileNotFound(String),
    #[error("Hash inválido para el track {0}")]
    InvalidHash(usize),
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AudioTrack {
    pub id: usize,
    pub name: String,
    pub path: String,
    pub hash: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OASFProject {
    pub bpm: f64,
    pub audio_tracks: Vec<AudioTrack>,
}

impl OASFProject {
    /// Abre un proyecto .oasf como lo haría un ingeniero en un estudio profesional.
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self, OASFError> {
        // Lógica para leer ZIP y validar hashes (mock por ahora)
        Ok(OASFProject {
            bpm: 120.0,
            audio_tracks: vec![
                AudioTrack {
                    id: 1,
                    name: "Kick".to_string(),
                    path: "audio/kick.wav".to_string(),
                    hash: "sha3-512:mockhash".to_string(),
                }
            ],
        })
    }
}