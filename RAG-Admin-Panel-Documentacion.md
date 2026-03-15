# RAG Admin Panel - Documentaci??n Actualizada (Marzo 2024)

Este documento detalla el uso, arquitectura y configuraci??n del panel de administraci??n RAG Multimodal, unificado para gestionar clientes y workflows en n8n.

## 1. Informaci??n General y Accesos

- **URL del Panel:** `https://admin.ticosys.com`
- **Contrase??a de Acceso:** `Buscaloserver01*`
- **Secret Key (Interno n8n):** `ticosys-rag-admin-2024`
- **Base de Datos Operativa:** `chatbot_saas` (PostgreSQL unificado).

## 2. Unificaci??n de Infraestructura (Importante)

Para evitar errores de sincronizaci??n, se han establecido las siguientes reglas:
1. **Min??sculas**: Todos los nombres de esquemas se fuerzan a min??sculas (ej: `ticosys_chatbot` en lugar de `Ticosys_Chatbot`).
2. **Schema ??nico**: Los datos residen exclusivamente en la base de datos `chatbot_saas`.
3. **Estructura RAG 2.0**: Las tablas `rag_docs` ahora soportan contenido multimodal (audio, video, imagen) con vectores de 3072 dimensiones (`halfvec`).

## 3. Workflows de n8n Operativos

### Administrador de Base de Datos y CRM
- **Nombre:** `ADMIN: RAG Database Manager`
- **ID:** `H5N1UoSIwLRqtMAI`
- **Webhook:** `https://n8n.ticosys.com/webhook/rag-admin-prod`

### Plantilla Maestra para Clonados
- **Nombre:** `TICOSYS- RAG Multimodal V2`
- **ID:** `55JnmvDr3zcVIwGK`
- *Nota: Al clonar, el sistema reemplaza autom??ticamente los placeholders `BASE_SCHEMA` y `BASE_TENANT` por los datos del nuevo cliente.*

## 4. Estructura de Tabla Est??ndar (RAG 2.0)

El sistema crea autom??ticamente la tabla con esta estructura para compatibilidad con Gemini Embedding 2:

```sql
CREATE TABLE <schema>.rag_docs (
    id SERIAL PRIMARY KEY,
    file_id TEXT,
    file_name TEXT,
    file_type TEXT,
    mime_type TEXT,
    content_text TEXT,
    metadata JSONB,
    embedding halfvec(3072)
);
```

---

*Documentaci??n actualizada seg??n la ??ltima configuraci??n de producci??n.*
