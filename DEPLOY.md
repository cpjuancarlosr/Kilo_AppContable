# FinAnalytix - Instrucciones de Despliegue

## 🚀 Inicio Rápido con Docker

La forma más fácil de ejecutar FinAnalytix es usando Docker Compose:

```bash
# 1. Clonar o navegar al directorio del proyecto
cd FinAnalytix

# 2. Copiar y configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus configuraciones

# 3. Construir y ejecutar todos los servicios
docker-compose up --build

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

Para detener los servicios:
```bash
docker-compose down
```

Para detener y eliminar volúmenes (⚠️ borra datos):
```bash
docker-compose down -v
```

## 🔧 Desarrollo Local

### Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate
# Activar (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos (requiere PostgreSQL)
# Crear base de datos 'finanalytix'

# Ejecutar migraciones (usar Alembic en producción)
# alembic upgrade head

# Iniciar servidor
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en http://localhost:8000
- Documentación API: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

### Frontend (Next.js)

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en http://localhost:3000

## 📁 Estructura del Proyecto

```
FinAnalytix/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── executive.py    # Capa Ejecutiva
│   │   │           ├── control.py      # Control Financiero
│   │   │           ├── fiscal.py       # Fiscal Estratégico
│   │   │           └── simulation.py   # Simulación
│   │   ├── core/              # Configuración y seguridad
│   │   ├── db/                # Base de datos
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Lógica de negocio
│   │   ├── financial_engine/  # Motor de cálculos
│   │   │   └── calculator.py
│   │   └── main.py            # Punto de entrada
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── dashboard/
│   │   │   │   ├── ejecutivo/
│   │   │   │   ├── control/
│   │   │   │   ├── fiscal/
│   │   │   │   └── simulacion/
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── layout/        # Sidebar, Header, Layout
│   │   │   └── ui/            # Componentes UI
│   │   ├── lib/               # API client, utilidades
│   │   └── types/             # TypeScript types
│   ├── Dockerfile
│   ├── package.json
│   └── tailwind.config.ts
│
├── docker-compose.yml
└── README.md
```

## 🔌 API Endpoints

### Capa Ejecutiva
- `GET /api/v1/executive/metrics` - Métricas ejecutivas
- `GET /api/v1/executive/alerts` - Alertas activas
- `GET /api/v1/executive/kpis` - KPIs principales

### Control Financiero
- `GET /api/v1/control/complete-analysis` - Análisis completo
- `GET /api/v1/control/vertical-analysis` - Análisis vertical
- `GET /api/v1/control/horizontal-analysis` - Análisis horizontal
- `GET /api/v1/control/ratios` - Ratios financieros
- `GET /api/v1/control/cash-conversion-cycle` - CCC
- `GET /api/v1/control/break-even` - Punto de equilibrio

### Fiscal Estratégico
- `GET /api/v1/fiscal/summary` - Resumen fiscal
- `GET /api/v1/fiscal/projection` - Proyección fiscal
- `GET /api/v1/fiscal/risk-assessment` - Evaluación de riesgo

### Simulación Estratégica
- `POST /api/v1/simulation/growth` - Simulación de crecimiento
- `POST /api/v1/simulation/pricing` - Simulación de precios
- `POST /api/v1/simulation/financing` - Simulación de financiamiento
- `POST /api/v1/simulation/expansion` - Simulación de expansión

### México - CFDI / SAT
- `POST /api/v1/mexico/empresa` - Registrar empresa mexicana
- `POST /api/v1/mexico/cfdi/calcular` - Calcular impuestos CFDI
- `GET /api/v1/mexico/cfdi/validar-rfc/{rfc}` - Validar RFC
- `POST /api/v1/mexico/retenciones/calcular` - Calcular retenciones ISR
- `GET /api/v1/mexico/retenciones/acreditables` - Retenciones acreditables
- `POST /api/v1/mexico/diot/calcular` - Calcular DIOT mensual
- `POST /api/v1/mexico/isr/proyeccion-anual` - Proyectar ISR anual
- `POST /api/v1/mexico/isr/pago-provisional` - Calcular pago provisional
- `GET /api/v1/mexico/catalogos/regimenes-fiscales` - Catálogo de regímenes
- `GET /api/v1/mexico/catalogos/usos-cfdi` - Catálogo de usos CFDI

### Importación de Datos (Estados de Cuenta)
- `POST /api/v1/advanced/importar-estado-cuenta` - Importar PDF/CSV/Excel bancario
  - Detecta automáticamente banco (BBVA, Santander, Banorte, etc.)
  - Categoriza transacciones (proveedores, nómina, impuestos, etc.)
  - Extrae RFCs de descripciones
  - Valida balance de saldos

### Executive Scorecard (Indicadores Críticos)
- `GET /api/v1/advanced/scorecard-ejecutivo` - Dashboard ejecutivo completo
  - Health Score financiero (0-100)
  - KPIs críticos con semáforo
  - Alertas predictivas
  - Recomendaciones de acción
- `GET /api/v1/advanced/scorecard/metricas-avanzadas` - Métricas avanzadas
  - Altman Z-Score (predicción de bancarrota)
  - Análisis DuPont (descomposición ROE)
  - Ratios de distress financiero
  - Eficiencia operativa
- `POST /api/v1/advanced/analisis-sensibilidad` - Análisis de sensibilidad
  - Impacto de cambios en ventas sobre utilidades
  - Escenarios optimista/pesimista
- `GET /api/v1/advanced/kpis-sectoriales` - Benchmarking por sector
- `GET /api/v1/advanced/tendencias` - Análisis de tendencias históricas

## 🇲🇽 Configuración Específica para México

### Tasas de Impuestos (2024)
- **IVA General**: 16%
- **IVA Fronterizo**: 8% (zonas fronterizas)
- **ISR Personas Morales**: 30%
- **ISR Personas Físicas**: Hasta 35%
- **IEPS**: Variable por producto (cerveza 50%, tabaco 160%, etc.)
- **Retención Arrendamiento**: 10%
- **Retención Honorarios**: 10%
- **Retención Dividendos**: 10%

### Zonas Fronterizas (IVA 8%)
El sistema detecta automáticamente si un código postal pertenece a zona fronteriza:
- Baja California
- Parte de Sonora
- Municipios fronterizos

### CFDI 4.0
Soporte completo para:
- Facturas de ingreso (I)
- Notas de crédito (E)
- Recibos de nómina (N)
- Complementos de pago (P)
- Cálculo automático de impuestos por concepto

### DIOT (Declaración Informativa)
Generación automática de:
- Operaciones con proveedores
- IVA acreditable y no acreditable
- Validación de excesos
- Formato para importación al SAT

### Retenciones
Cálculo y seguimiento de:
- ISR retenido por honorarios
- ISR retenido por arrendamiento
- ISR retenido por dividendos
- IVA retenido (2/3 partes)

## 🧪 Pruebas

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📊 Características Implementadas

### Capa Ejecutiva
- [x] Dashboard con métricas sintéticas
- [x] Alertas inteligentes
- [x] Variación interanual
- [x] Capital de trabajo

### Capa de Control Financiero
- [x] Análisis vertical y horizontal
- [x] Márgenes detallados
- [x] EBITDA
- [x] Punto de equilibrio
- [x] Ciclo de conversión de efectivo
- [x] Ratios financieros

### Capa Fiscal Estratégica
- [x] Carga fiscal efectiva
- [x] Proyección de impuestos
- [x] Evaluación de riesgo fiscal

### Capa de Simulación
- [x] Modelador de crecimiento
- [x] Simulador de precios
- [x] Impacto de financiamiento
- [x] Simulación de expansión

### México (SAT/CFDI)
- [x] Registro de empresas con RFC y régimen fiscal
- [x] Cálculo de CFDI 4.0 (IVA, IEPS, retenciones)
- [x] Validación de RFCs
- [x] Retenciones de ISR (honorarios, arrendamiento, dividendos)
- [x] DIOT mensual (operaciones con terceros)
- [x] Pagos provisionales de ISR
- [x] IVA fronterizo (8%)
- [x] Acreditamiento de impuestos
- [x] Catálogos SAT (regímenes, usos CFDI)

### Importación de Datos
- [x] Estados de cuenta PDF (BBVA, Santander, Banorte, etc.)
- [x] Importación CSV y Excel
- [x] Categorización automática de transacciones
- [x] Detección de transferencias internas
- [x] Extracción de RFCs
- [x] Validación de balances

### Indicadores Avanzados (Executive Scorecard)
- [x] Altman Z-Score (predicción de bancarrota)
- [x] Análisis DuPont (ROE descompuesto)
- [x] Cash Flow Quality (calidad de utilidades)
- [x] Ratios de distress financiero
- [x] Eficiencia operativa (CCC, DSO, DIO)
- [x] Análisis de sensibilidad
- [x] KPIs por sector (benchmarking)
- [x] Health Score financiero
- [x] Alertas predictivas con probabilidad
- [x] Recomendaciones de acción priorizadas

## 🔒 Seguridad

- Autenticación JWT implementada
- Hash de contraseñas con bcrypt
- CORS configurado
- Validación de entradas con Pydantic
- Preparado para HTTPS/TLS en producción

## 🚀 Despliegue en Producción

### Consideraciones
1. Usar PostgreSQL con backups automáticos
2. Configurar SSL/TLS
3. Usar Redis para caché y sesiones
4. Implementar rate limiting
5. Configurar monitoreo (Prometheus/Grafana)
6. Usar Nginx como reverse proxy

### Importación de Estados de Cuenta
FinAnalytix puede importar estados de cuenta de los principales bancos mexicanos:

**Bancos soportados:**
- BBVA Bancomer
- Santander
- Banorte
- Banamex (Citibanamex)
- HSBC
- Scotiabank
- Banco Azteca
- Inbursa
- Afirme
- Banregio

**Formatos soportados:**
- PDF (descargado de banca electrónica)
- CSV (exportación de Excel)
- Excel (.xlsx, .xls)

**Proceso de importación:**
1. El sistema detecta automáticamente el banco
2. Extrae todas las transacciones
3. Categoriza automáticamente (proveedores, nómina, impuestos, etc.)
4. Detecta RFCs en descripciones
5. Valida que los saldos cuadren
6. Sugiere conciliación contable

### Análisis Avanzado
El Executive Scorecard proporciona:

**Health Score (0-100):**
- 85-100: Salud excelente
- 70-84: Salud buena
- 55-69: Atención requerida
- 40-54: Acción necesaria
- 0-39: Intervención urgente

**Altman Z-Score:**
- > 3.0: Zona segura
- 1.8 - 3.0: Zona gris
- < 1.8: Zona de distress (riesgo de bancarrota)

**Análisis DuPont:**
Descompone ROE en:
- Margen neto (eficiencia operativa)
- Rotación de activos (eficiencia de activos)
- Multiplicador de capital (apalancamiento)

### Variables de Entorno Requeridas
```env
SECRET_KEY=<clave-secreta-fuerte>
DATABASE_URL=<url-de-produccion>
CORS_ORIGINS=["https://tu-dominio.com"]
```

## 📞 Soporte

Para reportar issues o solicitar features, usar el sistema de issues del repositorio.
