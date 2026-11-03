# Banco de Chile - CMF & Operational Risk AI Governance Platform 🏦⚖️

Plataforma Multi-Agente de Gobierno Operacional, Cumplimiento Normativo CMF (Ley 20.009 de Fraudes) y Trazabilidad de Auditoría en Tiempo Real.

---

## 🎯 Objetivo de la Solución
Automatizar la gestión de reclamos regulados por la **Comisión para el Mercado Financiero (CMF)** y eventos de fraude operacional, reduciendo el tiempo de resolución de días a segundos y asegurando trazabilidad en SQL para auditorías.

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Función |
| :--- | :--- | :--- |
| **Python 3.11+** | Lenguaje Principal | Lógica de orquestación de agentes y motor normativo. |
| **FastAPI** | REST Web Framework | Endpoints asíncronos para ingesta de reclamos. |
| **Pandas & SQLite** | Datos & Trazabilidad | Almacenamiento relacional de decisiones y métricas. |
| **Power Platform Ready** | OpenAPI Specification | Contrato listo para integrarse con **Power Automate** y **Power Apps**. |

---

## 🚀 Ejecución Local

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```
Swagger UI disponible en: http://127.0.0.1:8000/docs
