"""
Servicio de análisis de llamadas para generar resúmenes automáticos.
"""

import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict

from domain.entities import Call, CallSummary, Segment
from domain.models import Objection


class CallAnalyzer:
    """Servicio para analizar llamadas y generar resúmenes"""

    def __init__(self):
        # Palabras clave para detectar temas principales
        self.topic_keywords = {
            "precio": ["precio", "costo", "coste", "presupuesto", "inversión", "pagar", "caro", "barato"],
            "tiempo": ["tiempo", "cuándo", "fecha", "pronto", "ahora", "luego", "esperar"],
            "funcionalidad": ["funciona", "características", "features", "capacidades", "hacer"],
            "soporte": ["soporte", "ayuda", "asistencia", "técnico", "problemas"],
            "integración": ["integrar", "conectar", "api", "sistema", "plataforma"],
            "seguridad": ["seguridad", "privacidad", "datos", "proteger", "confidencial"],
            "escalabilidad": ["crecer", "escalar", "usuarios", "volumen", "capacidad"]
        }

    def analyze_call(self, call: Call) -> CallSummary:
        """Analizar una llamada completa y generar resumen"""
        segments = call.segments
        objections = call.objections or []

        # Métricas básicas
        total_segments = len(segments)
        total_objections = len(objections)

        # Análisis de tipos de objeciones
        objection_types = defaultdict(int)
        for objection in objections:
            objection_types[objection.type] += 1

        # Análisis de tiempo hablado por speaker
        speakers_time = defaultdict(int)
        last_ts = {}

        for segment in sorted(segments, key=lambda s: s.ts_ms):
            speaker = segment.speaker
            if speaker in last_ts:
                # Calcular duración aproximada del segmento anterior
                duration = segment.ts_ms - last_ts[speaker]
                speakers_time[speaker] += max(0, duration)
            last_ts[speaker] = segment.ts_ms

        # Detectar temas principales
        top_topics = self._detect_topics(segments)

        # Generar próximos pasos
        next_steps = self._generate_next_steps(call)

        # Calcular score de confianza
        confidence_score = self._calculate_confidence_score(call)

        return CallSummary(
            call_id=call.call_id,
            total_segments=total_segments,
            total_objections=total_objections,
            objection_types=dict(objection_types),
            speakers_time=dict(speakers_time),
            top_topics=top_topics,
            next_steps=next_steps,
            generated_at=datetime.now(),
            confidence_score=confidence_score
        )

    def _detect_topics(self, segments: List[Segment]) -> List[str]:
        """Detectar temas principales discutidos en la llamada"""
        topic_scores = defaultdict(int)
        total_words = 0

        for segment in segments:
            text = segment.text.lower()
            words = text.split()
            total_words += len(words)

            # Contar ocurrencias de palabras clave por tema
            for topic, keywords in self.topic_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        topic_scores[topic] += 1

        # Normalizar por longitud del texto y seleccionar top 3
        if total_words > 0:
            normalized_scores = {
                topic: score / total_words
                for topic, score in topic_scores.items()
            }
        else:
            normalized_scores = topic_scores

        # Ordenar por score y tomar top 3
        sorted_topics = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, score in sorted_topics[:3] if score > 0]

    def _generate_next_steps(self, call: Call) -> List[str]:
        """Generar próximos pasos recomendados basados en la llamada"""
        next_steps = []
        objections = call.objections or []

        # Si hay objeciones sin resolver, sugerir seguimiento
        unresolved_objections = [o for o in objections if o.confidence > 0.7]
        if unresolved_objections:
            next_steps.append("Agendar seguimiento para resolver objeciones pendientes")

        # Si se mencionó precio, sugerir propuesta
        price_objections = [o for o in objections if o.type == "precio"]
        if price_objections:
            next_steps.append("Enviar propuesta económica personalizada")

        # Si se mencionó autoridad, sugerir reunión con decisor
        authority_objections = [o for o in objections if o.type == "autoridad"]
        if authority_objections:
            next_steps.append("Coordinar reunión con el decisor")

        # Si no hay objeciones, sugerir siguiente paso en el proceso
        if not objections:
            next_steps.append("Enviar información adicional solicitada")
            next_steps.append("Agendar demo o presentación del producto")

        # Siempre incluir feedback
        next_steps.append("Enviar resumen de la llamada por email")

        return next_steps[:3]  # Máximo 3 próximos pasos

    def _calculate_confidence_score(self, call: Call) -> float:
        """Calcular score de confianza en el análisis"""
        if not call.segments:
            return 0.0

        # Factores que afectan la confianza
        confidence_factors = []

        # 1. Número de segmentos (más = mejor)
        segment_factor = min(len(call.segments) / 20.0, 1.0)  # Máximo con 20 segmentos
        confidence_factors.append(segment_factor)

        # 2. Calidad de transcripción (promedio de confidence)
        if call.segments:
            avg_confidence = sum(s.confidence for s in call.segments) / len(call.segments)
            confidence_factors.append(avg_confidence)

        # 3. Presencia de objeciones claras
        objection_factor = 1.0 if call.objections else 0.5
        confidence_factors.append(objection_factor)

        # 4. Balance de participación (ambos speakers hablaron)
        speakers = set(s.speaker for s in call.segments)
        balance_factor = 1.0 if len(speakers) >= 2 else 0.7
        confidence_factors.append(balance_factor)

        # Promedio ponderado
        weights = [0.2, 0.3, 0.3, 0.2]  # Pesos para cada factor
        confidence_score = sum(f * w for f, w in zip(confidence_factors, weights))

        return round(confidence_score, 2)
