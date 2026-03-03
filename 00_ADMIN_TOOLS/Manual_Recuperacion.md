# Manual de Recuperación Maestra - Protocolo Fénix
**Instrucciones para Gerencia / Equipo Comercial (Sergio)**

Este manual detalla los pasos exactos que debes realizar si una inmobiliaria (Licenciataria) reporta la pérdida, robo o compromiso severo de su Llave USB Guanes Inmobiliaria.

Ante la pérdida, la unidad perdida activa automáticamente el "Instinto de Preservación" (*Scorched Earth*), encriptando y destruyendo el componente algorítmico local para evitar robo de datos. Sin embargo, los Contratos en Solana siguen bloqueados asumiendo que esa USB poseía la Llave C.

Para recuperar la gobernanza comercial y técnica, debes escalar el caso al Cuartel General (Arquitecto) entregando esta información de 3 pasos:

### PASO 1: Notificar el ID Perdido
Busca en tu Dashboard de licenciatarios en N8N la agencia afectada.
- **Debes enviarme por canal seguro (Signal) el `USB_ID` de la unidad robada.**
- *Acción en Headquarters:* Ejecutaré la revocación (`SetAuthority`) en Solana para deshabilitar para siempre que el dispositivo perdido intente firmar liberaciones.

### PASO 2: Preparar el Reemplazo Virgen
Toma una USB física nueva en la oficina y prepara la instalación de Guanes V5.
- **Debes enviarme el nuevo `USB_ID` impreso en el hardware o auto-generado por el sistema.**
- **Pídele a la inmobiliaria su dirección pública de Wallet Solana.**
- *Acción en Headquarters:* Traspasaré la Autoridad de los contratos huérfanos a esta nueva billetera y la ataré al nuevo `USB_ID`. 

### PASO 3: Re-inyección de la Base de Datos
- **Mantén la USB nueva conectada al servidor del Headquarters.**
- *Acción en Headquarters:* Descargaré todo el historial de contratos en formato JSON desde nuestro cluster central respaldado por N8N y lo inyectaré directamente a la base de datos ofuscada `.sys_guanes_usb.db` de la nueva unidad.
- **Resultado Final:** Te entregaré la USB nueva. Cuando la envíes a la agencia, ellos la conectarán e inmediatamente verán reflejado todo su historial de bóvedas Escrow como si nada hubiera pasado (Resiliencia).
