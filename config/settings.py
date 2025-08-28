"""
Configuración centralizada usando Pydantic para validación y tipos.
"""

from typing import Optional
try:
    from pydantic import BaseSettings, Field
except ImportError:
    from pydantic_settings import BaseSettings
    from pydantic import Field


class AudioConfig(BaseSettings):
    """Configuración de audio"""
    mic_name_substr: str = Field(default="Blue Snowball", env="MIC_NAME_SUBSTR")
    spk_name_substr: str = Field(default="PRO", env="SPK_NAME_SUBSTR")
    frame_ms: int = Field(default=20, env="FRAME_MS")
    mic_gain: float = Field(default=3.0, env="MIC_GAIN")
    loop_gain: float = Field(default=8.0, env="LOOP_GAIN")
    vad_threshold: float = Field(default=0.01, env="VAD_THRESHOLD")
    vad_enabled: bool = Field(default=True, env="VAD_ENABLED")
    normalize_enabled: bool = Field(default=True, env="NORMALIZE_ENABLED")
    normalize_target_level: float = Field(default=0.7, env="NORMALIZE_TARGET_LEVEL")
    resample_method: str = Field(default="poly", env="RESAMPLE_METHOD")


class DeepgramConfig(BaseSettings):
    """Configuración de Deepgram"""
    api_key: str = Field(default="tu_api_key_aqui", env="DEEPGRAM_API_KEY")
    model: str = Field(default="nova-3-general", env="DEEPGRAM_MODEL")
    language: str = Field(default="multi", env="DEEPGRAM_LANGUAGE")
    encoding: str = Field(default="linear16", env="DEEPGRAM_ENCODING")
    sample_rate: int = Field(default=16000, env="DEEPGRAM_SAMPLE_RATE")
    multichannel: bool = Field(default=True, env="DEEPGRAM_MULTICHANNEL")
    smart_format: bool = Field(default=True, env="DEEPGRAM_SMART_FORMAT")

    # NOVA 3 Features
    interim_results: bool = Field(default=True, env="DEEPGRAM_INTERIM_RESULTS")
    endpointing: bool = Field(default=True, env="DEEPGRAM_ENDPOINTING")
    pii_redact: bool = Field(default=False, env="DEEPGRAM_PII_REDACT")
    diarize: bool = Field(default=False, env="DEEPGRAM_DIARIZE")
    utterance_end_ms: int = Field(default=1000, env="DEEPGRAM_UTTERANCE_END_MS")
    vad_events: bool = Field(default=True, env="DEEPGRAM_VAD_EVENTS")
    no_delay: bool = Field(default=False, env="DEEPGRAM_NO_DELAY")
    numerals: bool = Field(default=True, env="DEEPGRAM_NUMERALS")
    profanity_filter: bool = Field(default=False, env="DEEPGRAM_PROFANITY_FILTER")


class ConnectionConfig(BaseSettings):
    """Configuración de conexión"""
    region: str = Field(default="us", env="DG_REGION")
    base_wss: str = Field(default="wss://api.deepgram.com", env="DG_BASE_WSS")
    reconnect_enabled: bool = Field(default=True, env="RECONNECT_ENABLED")
    reconnect_delay: float = Field(default=3.0, env="RECONNECT_DELAY")
    max_reconnect_attempts: int = Field(default=5, env="MAX_RECONNECT_ATTEMPTS")


class LoggingConfig(BaseSettings):
    """Configuración de logging"""
    rms_interval: int = Field(default=100, env="LOG_RMS_INTERVAL")
    events: bool = Field(default=True, env="LOG_EVENTS")
    transcript: bool = Field(default=True, env="LOG_TRANSCRIPT")
    debug: bool = Field(default=False, env="LOG_DEBUG")


class AudioModeConfig(BaseSettings):
    """Configuración de modo de audio"""
    mode: str = Field(default="stereo", env="AUDIO_MODE")
    stereo_layout: str = Field(default="LR", env="STEREO_LAYOUT")


class AppConfig(BaseSettings):
    """Configuración completa de la aplicación"""
    # Audio Configuration
    mic_name_substr: str = Field(default="Blue Snowball", env="MIC_NAME_SUBSTR")
    spk_name_substr: str = Field(default="PRO", env="SPK_NAME_SUBSTR")
    frame_ms: int = Field(default=20, env="FRAME_MS")
    mic_gain: float = Field(default=3.0, env="MIC_GAIN")
    loop_gain: float = Field(default=8.0, env="LOOP_GAIN")
    vad_threshold: float = Field(default=0.01, env="VAD_THRESHOLD")
    vad_enabled: bool = Field(default=True, env="VAD_ENABLED")
    normalize_enabled: bool = Field(default=True, env="NORMALIZE_ENABLED")
    normalize_target_level: float = Field(default=0.7, env="NORMALIZE_TARGET_LEVEL")
    resample_method: str = Field(default="poly", env="RESAMPLE_METHOD")

    # Deepgram Configuration
    deepgram_api_key: str = Field(default="tu_api_key_aqui", env="DEEPGRAM_API_KEY")
    deepgram_model: str = Field(default="nova-3-general", env="DEEPGRAM_MODEL")
    deepgram_language: str = Field(default="multi", env="DEEPGRAM_LANGUAGE")
    deepgram_encoding: str = Field(default="linear16", env="DEEPGRAM_ENCODING")
    deepgram_sample_rate: int = Field(default=16000, env="DEEPGRAM_SAMPLE_RATE")
    deepgram_multichannel: bool = Field(default=True, env="DEEPGRAM_MULTICHANNEL")
    deepgram_smart_format: bool = Field(default=True, env="DEEPGRAM_SMART_FORMAT")
    deepgram_interim_results: bool = Field(default=True, env="DEEPGRAM_INTERIM_RESULTS")
    deepgram_endpointing: bool = Field(default=True, env="DEEPGRAM_ENDPOINTING")
    deepgram_pii_redact: bool = Field(default=False, env="DEEPGRAM_PII_REDACT")
    deepgram_diarize: bool = Field(default=False, env="DEEPGRAM_DIARIZE")
    deepgram_utterance_end_ms: int = Field(default=1000, env="DEEPGRAM_UTTERANCE_END_MS")
    deepgram_vad_events: bool = Field(default=True, env="DEEPGRAM_VAD_EVENTS")
    deepgram_no_delay: bool = Field(default=False, env="DEEPGRAM_NO_DELAY")
    deepgram_numerals: bool = Field(default=True, env="DEEPGRAM_NUMERALS")
    deepgram_profanity_filter: bool = Field(default=False, env="DEEPGRAM_PROFANITY_FILTER")

    # Connection Configuration
    dg_region: str = Field(default="us", env="DG_REGION")
    dg_base_wss: str = Field(default="wss://api.deepgram.com", env="DG_BASE_WSS")
    reconnect_enabled: bool = Field(default=True, env="RECONNECT_ENABLED")
    reconnect_delay: float = Field(default=3.0, env="RECONNECT_DELAY")
    max_reconnect_attempts: int = Field(default=5, env="MAX_RECONNECT_ATTEMPTS")

    # Audio Mode Configuration
    audio_mode: str = Field(default="stereo", env="AUDIO_MODE")
    stereo_layout: str = Field(default="LR", env="STEREO_LAYOUT")

    # Logging Configuration
    log_rms_interval: int = Field(default=100, env="LOG_RMS_INTERVAL")
    log_events: bool = Field(default=True, env="LOG_EVENTS")
    log_transcript: bool = Field(default=True, env="LOG_TRANSCRIPT")
    log_debug: bool = Field(default=False, env="LOG_DEBUG")

    # Sales Coaching Configuration
    use_llm_fallback: bool = Field(default=True, env="USE_LLM_FALLBACK")
    llm_model: str = Field(default="gpt-5-nano", env="LLM_MODEL")
    llm_timeout_sec: float = Field(default=0.8, env="LLM_TIMEOUT_SEC")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    playbook_json: str = Field(default="data/playbook.json", env="PLAYBOOK_JSON")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
config = AppConfig()
