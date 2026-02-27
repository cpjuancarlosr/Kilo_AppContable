# FinAnalytix - Plataforma de Análisis Financiero Empresarial

Aplicación web progresiva (PWA) para análisis financiero, fiscal y estratégico empresarial.

## 🏗️ Arquitectura del Proyecto

```
FinAnalytix/
├── backend/                    # FastAPI + Python
│   ├── app/
│   │   ├── api/v1/endpoints/  # Rutas API
│   │   ├── core/              # Configuración y seguridad
│   │   ├── db/                # Conexión y sesiones
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Lógica de negocio
│   │   └── financial_engine/  # Motor de cálculos financieros
│   ├── tests/
│   └── Dockerfile
├── frontend/                   # Next.js + React + TypeScript
│   ├── src/
│   │   ├── app/               # Rutas de Next.js App Router
│   │   ├── components/        # Componentes React
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilidades
│   │   └── types/             # TypeScript types
│   ├── public/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Inicio Rápido

### Con Docker
```bash
docker-compose up --build
```

### Backend (desarrollo)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (desarrollo)
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentación

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
