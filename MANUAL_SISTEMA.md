# 📕 MANUAL DEL SISTEMA: AbogadoVirtual (V5 - 2026)

Este manual es tu guía rápida para mantener el sistema operativo y entender su arquitectura de ingeniería jurídica.

## 🚀 Cómo Iniciar el Sistema (Híbrido Local-Nube)
Para que el Chat y el Cerebro de la IA funcionen, simplemente ejecuta el archivo del escritorio:
- **`ARRANCAR_GUANES.bat`**

Esto abrirá tres componentes críticos:
1.  **Cerebro RAG (Puerto 8000)**: Procesa leyes (ChromaDB) y plantillas usando el modelo **Qwen3:8b**.
2.  **Túnel (Ngrok)**: Conecta tu PC local con el webhook de N8N en la nube.
3.  **Guardián**: Vigila que los servidores Flask y Ollama no se detengan.

## 🛡️ Reglas de Negocio: Blindaje USB
El sistema cuenta con un **Protocolo de Protección de Valor (Blindaje USB)**:
- **Venta Automatizada**: Consultas laborales, civiles y de salud comunes se resuelven con minutas de **$19.900**.
- **Blindaje Premium**: Los temas de **Propiedad Horizontal (Sergio), Construcción (Olga), Minería y Glosas de Salud** están bloqueados para venta automática. La IA está instruida para remitir estos casos a una **"Consulta Experta"** para proteger el valor de las asesorías técnicas.

## 📁 Estructura del Proyecto
- `01_Ingesta_Datos`: Entrada y limpieza de nueva jurisprudencia.
- `03_Motor_Core`: El corazón RAG (Incluye `GuanesEngine` y base vectorial `db_guanes`).
- `07_Cloud_Abogado`: Interfaz web y **Bóveda de Minutas** (`minutas_cloud.db`).
- `08_Tablero_Interno`: Monitor de métricas y auditoría en tiempo real.
- `99_Logs_y_Temporales`: El registro de telemetría y salud del sistema.

## 🤖 Instrucción para IAs Externas
> "Este sistema es una arquitectura HÍBRIDA 2026. El servidor puente corre en el puerto 8000. El motor RAG utiliza ChromaDB para persistencia y Ollama (Qwen3:8b) para inferencia. Se debe respetar estrictamente el Blindaje USB en todas las respuestas del chat."

## 💳 Flujo de Cobro (Wompi)
- **Link único de pago**: `https://checkout.wompi.co/l/y0fJnm` ($19.900 COP)
- **URL de redirección post-pago**: `https://abogado.guanes.biz/gracias`
- **Webhook de confirmación**: `https://n8n-production-612f.up.railway.app/webhook/pago-confirmado`
- **Alerta al abogado**: WhatsApp vía CallMeBot (apikey: `1852153`, número: `573012428215`)
- **Workflow N8N**: `99_Logs_y_Temporales/workflow_pago_confirmado.json`

## ✅ Checklist de Activación en Producción
- [ ] `ollama pull qwen3:8b-q4_K_M`
- [ ] `ollama create guanes-senior -f GuanesModel.Modelfile` (raíz del proyecto)
- [ ] Importar `workflow_pago_confirmado.json` en N8N de Railway
- [ ] Configurar redirect y webhook en panel Wompi link `y0fJnm`
- [ ] Deploy de `index.html` y `gracias.html` a Vercel/Railway

---
*Diseñado por Antigravity para Guanes IA - Marzo 2026*
