/**
 * CODEX GARANTÍA DIGITAL - FRONTEND LOGIC
 * Handles Calculator, Disclaimer Validation, and PDF Generation
 */

// CONFIGURATION
const COSTO_INMOBILIARIA_PCT = 1.20; // 120% of one canon (approx 10% * 12)
const COSTO_CODEX_PCT = 0.15; // 15% One time fee
const VAULT_ADDRESS = "HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH"; // Placeholder or Real if provided

const CLAUSULA_RETENCION_DEPOSITO = `CLÁUSULA DE GARANTÍA REAL Y DERECHO DE RETENCIÓN (ART. 1177 C.Co): "Las Partes acuerdan que el presente contrato se rige por las normas del DEPÓSITO MERCANTIL y servicios logísticos conexos. En consecuencia, de conformidad con el Artículo 1177 del Código de Comercio, EL OPERADOR LOGÍSTICO (Guanes/Beneficiario) tendrá DERECHO DE RETENCIÓN sobre todas las mercancías, bienes, enseres o inventarios depositados por EL CLIENTE en el área designada.

PARÁGRAFO DE EJECUCIÓN: En caso de mora superior a 5 días en el pago de la Tarifa de Almacenaje, EL OPERADOR podrá bloquear el acceso a la bodega y retener la mercancía. Si la mora persiste por 30 días, EL CLIENTE autoriza expresamente, mediante este mandato irrevocable, la venta directa o subasta privada de las mercancías retenidas para cubrir el valor de la deuda, gastos de cobranza y costos operativos, renunciando a cualquier requerimiento judicial previo."`;

const CLAUSULA_RENUNCIA_PRIMA = `CLÁUSULA DE NATURALEZA ATÍPICA Y RENUNCIA A DERECHOS DE ARRENDAMIENTO: "Las Partes declaran expresamente que el presente vínculo jurídico corresponde a un CONTRATO DE CONCESIÓN DE ESPACIO COMERCIAL (Coworking/Pop-Up) y no a un arrendamiento de local comercial. La causa del contrato es la prestación de servicios integrales (Seguridad, Marketing del Centro, Aseo, Conectividad) donde el espacio físico es meramente instrumental.

RENUNCIA EXPRESA: En virtud de la autonomía de la voluntad y la naturaleza atípica de este contrato, EL CONCESIONARIO (Ocupante) manifiesta conocer que NO LE SON APLICABLES las disposiciones de los Artículos 518 a 524 del Código de Comercio. En consecuencia, RENUNCIA expresamente a reclamar:

1. Derecho a la renovación automática del contrato.
2. Prima comercial o 'Goodwill' por acreditación del establecimiento.
3. Indemnizaciones por terminación unilateral o no renovación al vencimiento del plazo pactado."`;

const CLAUSULA_GESTION_REMOTA = `CLÁUSULA DE MANDATO DE GESTIÓN REMOTA: "EL BENEFICIARIO declara conocer que el servicio prestado por GUANES LEGALTECH es de naturaleza Tecnológica, Financiera y Jurídica. En consecuencia, GUANES LEGALTECH NO asume obligaciones de mandatario general sobre el cuidado material del inmueble.

Quedan expresamente excluidas del mandato:

1. Visitas de inspección ocular o inventarios físicos.
2. Gestión de llaves, reparaciones, aseo o mantenimiento.
3. Atención de emergencias locativas (plomería, electricidad, etc.). EL BENEFICIARIO conserva la guarda material del bien y libera a GUANES de cualquier responsabilidad por deterioro físico del inmueble."`;

// --- CALCULATOR LOGIC ---
function calcularAhorro() {
    const canonInput = document.getElementById('canonMensual').value;
    const canon = parseFloat(canonInput);

    if (isNaN(canon) || canon <= 0) {
        alert("Por favor ingresa un valor de canon válido.");
        return;
    }

    // Calculations
    const costoInmobiliaria = canon * COSTO_INMOBILIARIA_PCT; // Costo anual estimado
    const costoCodex = canon * COSTO_CODEX_PCT; // Pago único
    const ahorro = costoInmobiliaria - costoCodex;

    // Display Results
    document.getElementById('valInmobiliaria').innerText = formatCurrency(costoInmobiliaria);
    document.getElementById('valCodex').innerText = formatCurrency(costoCodex);

    const ahorroEl = document.getElementById('valAhorro');
    ahorroEl.innerText = formatCurrency(ahorro);

    // Animate display
    document.getElementById('ahorroResult').classList.add('active');
    ahorroEl.style.animation = "pulse 0.5s ease-in-out";
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value);
}

// --- VAULT LOGIC ---
document.addEventListener('DOMContentLoaded', () => {
    // Set Address
    const addressEl = document.getElementById('vaultAddress');
    if (addressEl) {
        addressEl.innerText = VAULT_ADDRESS;
    }
});

function copiarAddress() {
    navigator.clipboard.writeText(VAULT_ADDRESS).then(() => {
        alert("Dirección de Bóveda copiada al portapapeles.");
    }).catch(err => {
        console.error('Error al copiar: ', err);
    });
}

// --- FORM & PDF GENERATION ---
// --- WEB3 LOGIC ---
async function connectWalletAndSign() {
    if (window.solana && window.solana.isPhantom) {
        try {
            // Connect
            const resp = await window.solana.connect();
            const publicKey = resp.publicKey.toString();
            console.log("Connected to Phantom:", publicKey);

            // Simulation of Signing a Message
            const message = `Firma Digital Protocolo Guanes: Acepto términos y condiciones. Wallet: ${publicKey}`;
            const encodedMessage = new TextEncoder().encode(message);
            const signedMessage = await window.solana.signMessage(encodedMessage, "utf8");

            return { connected: true, publicKey: publicKey };
        } catch (err) {
            console.error(err);
            alert("Error al conectar Billetera: " + err.message);
            return { connected: false };
        }
    } else {
        alert("Phantom Wallet no encontrada. Por favor instálala para continuar.");
        window.open("https://phantom.app/", "_blank");
        return { connected: false };
    }
}

// --- FORM & PDF GENERATION ---
function toggleServices() {
    const tipo = document.getElementById('k_tipo_uso').value;
    const serviciosDiv = document.getElementById('servicios-conexos');
    const contractLabel = document.getElementById('term-contract-type');

    // Update Legal Text dynamically
    if (contractLabel) {
        if (tipo === 'vivienda_fianza') contractLabel.innerText = "Fianza Digital de Arrendamiento (Ley 820)";
        else if (tipo === 'comercio_bodega') contractLabel.innerText = "Código de Comercio (Local/Bodega)";
        else if (tipo === 'garantia_obras') contractLabel.innerText = "Póliza de Cumplimiento (Civil)";
    }

    // Hide originally, only show for specific if needed, but for now we simplify
    serviciosDiv.style.display = 'none';
}

const form = document.getElementById('kycForm');
if (form) {
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Validate Checkbox
        const isLegalChecked = document.getElementById('k_legal_check').checked;
        const isNoBricksChecked = document.getElementById('k_no_bricks_check').checked;

        if (!isLegalChecked || !isNoBricksChecked) {
            alert("Debes aceptar los términos legales, la cesión de rendimientos y la cláusula de gestión remota para continuar.");
            return;
        }

        // WEB3 CONNECTION TRIGGER
        const walletAuth = await connectWalletAndSign();
        if (!walletAuth.connected) return; // Stop if not connected

        const tipoUso = document.getElementById('k_tipo_uso').value;
        let serviciosSeleccionados = []; // Simplified for V2

        // Get Data
        const data = {
            tipo: tipoUso,
            servicios: serviciosSeleccionados.join(', '),
            nombre: document.getElementById('k_nombre').value,
            cedula: document.getElementById('k_cedula').value,
            telefono: document.getElementById('k_telefono').value,
            email: document.getElementById('k_email').value,
            ciudad: document.getElementById('k_ciudad').value,
            wallet: walletAuth.publicKey // Save wallet for PDF
        };

        // Generate PDF
        await generateContractPDF(data);
    });
}

async function generateContractPDF(data) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Fonts & Styles
    doc.setFont("helvetica");

    // TITLE & CONTENT SELECTION
    let title = "";
    let bodyText = "";
    const dateStr = new Date().toLocaleDateString();

    const CLAUSULA_FIANZA_LIMITADA = `CLÁUSULA DE FIANZA LIMITADA: MANUEL ENRIQUE PRADA FORERO (GUANES LEGALTECH) actúa exclusivamente como custodio tecnológico y garante digital. Su responsabilidad financiera se limita estrictamente al monto de los activos digitales depositados en la Smart Vault. Agotados estos recursos, se extingue cualquier obligación de pago.`;

    const OPERADOR_INFO = "MANUEL ENRIQUE PRADA FORERO, identificado con C.C. 91.200.415 y T.P. 176.633 del C.S.J.";

    if (data.tipo === 'vivienda_fianza') {
        title = "FIANZA DIGITAL DE ARRENDAMIENTO DE VIVIENDA URBANA";
        bodyText = `
    Ciudad de Firma: ${data.ciudad}
    
    Entre los suscritos a saber: POR UNA PARTE, ${OPERADOR_INFO} (en adelante EL FIADOR DIGITAL), y POR OTRA PARTE, ${data.nombre} identificado con C.C. ${data.cedula} (en adelante EL ARRENDATARIO), hemos convenido celebrar el presente CONTRATO DE FIANZA, conexo al contrato de arrendamiento de vivienda urbana:

    PRIMERA. OBJETO: El presente contrato constituye una GARANTÍA DE PAGO sobre los cánones de arrendamiento, regida por la autonomía de la voluntad y supletoriamente por la Ley 820 de 2003.

    SEGUNDA. ${CLAUSULA_GESTION_REMOTA}

    TERCERA. GARANTÍA DIGITAL: El ARRENDATARIO constituye una garantía mediante depósito de activos digitales (USDC) en la Bóveda Multisig designada. Wallet Firmante: ${data.wallet || 'N/A'}

    CUARTA. CUSTODIA Y RENDIMIENTOS: Los fondos serán custodiados en protocolos seguros (Kamino/Save). 
    
    DISTRIBUCIÓN FINAL: El ARRENDATARIO recibirá la devolución del capital inicial (Principal) al término del contrato, siempre que se presente el paz y salvo. El ARRENDATARIO cede irrevocablemente a favor de EL FIADOR DIGITAL todos los rendimientos o intereses generados por dicho capital durante la custodia como remuneración del servicio.

    QUINTA. EJECUCIÓN: En caso de impago reportado por el Beneficiario, EL FIADOR procederá al pago directo utilizando los fondos en custodia.

    SEXTA. ${CLAUSULA_FIANZA_LIMITADA}
        `;
    } else if (data.tipo === 'comercio_bodega') {
        title = "CONTRATO DE ARRENDAMIENTO COMERCIAL (BODEGA/LOCAL)";
        bodyText = `
    Ciudad de Firma: ${data.ciudad}

    Entre los suscritos, ${OPERADOR_INFO} (EL ARRENDADOR TECNOLÓGICO) y ${data.nombre} con Nit/CC ${data.cedula} (EL ARRENDATARIO), celebran este CONTRATO DE ARRENDAMIENTO COMERCIAL:

    PRIMERA. OBJETO Y REGULACIÓN: El presente contrato se rige íntegramente por el CÓDIGO DE COMERCIO. Las partes gozan de libertad contractual para fijar garantías. Wallet Firmante: ${data.wallet || 'N/A'}

    SEGUNDA. ${CLAUSULA_GESTION_REMOTA}

    TERCERA. GARANTÍA LÍQUIDA: Se constituye garantía en USDC custodiada en Bóveda Multisig.

    CUARTA. DERECHO DE RETENCIÓN: ${CLAUSULA_RETENCION_DEPOSITO}

    QUINTA. ${CLAUSULA_FIANZA_LIMITADA}
        `;
    } else if (data.tipo === 'garantia_obras') {
        title = "PÓLIZA PRIVADA DE CUMPLIMIENTO Y SERVICIOS";
        bodyText = `
    Ciudad de Firma: ${data.ciudad}

    TOMADOR/GARANTIZADO: ${data.nombre} (ID: ${data.cedula}).
    BENEFICIARIO: Propietario / Contratante del Servicio.
    CUSTODIO: ${OPERADOR_INFO}.

    PRIMERA. OBJETO DE LA GARANTÍA: La presente Póliza Privada Digital garantiza el cumplimiento de las obligaciones derivadas del contrato de servicios/obra subyacente, hasta por el monto depositado en USDC. Wallet Firmante: ${data.wallet || 'N/A'}

    SEGUNDA. CUSTODIA MULTISIG (2 de 3): Los fondos reposan en una bóveda de firmas conjuntas. Para cualquier movimiento se requiere la firma del Árbitro (Manuel E. Prada) y una de las partes.

    TERCERA. EJECUCIÓN: El incumplimiento probado activará la transferencia de los fondos al Beneficiario.

    CUARTA. ${CLAUSULA_FIANZA_LIMITADA}
        `;
    }

    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text(title, 105, 20, null, null, "center");

    // BODY
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');

    const margin = 20;
    let y = 40;
    const lineHeight = 7;
    const pageWidth = 170;

    // Common footer or final text could be added here
    const fullText = bodyText + `\n\nFirmado digitalmente el ${dateStr}.\nFirma Biométrica/Wallet: ${data.wallet || 'Pending'}`;

    const splitText = doc.splitTextToSize(fullText, pageWidth);
    doc.text(splitText, margin, y);

    // SIGNATURE MOCKUP
    y += (splitText.length * lineHeight) + 20;
    doc.text("__________________________", margin, y);
    doc.text(`Firma: ${data.nombre} `, margin, y + 10);
    doc.text(`ID: ${data.cedula} `, margin, y + 15);

    // SAVE
    doc.save(`Contrato_${data.tipo}_${data.cedula}.pdf`);

    alert(`Contrato de ${data.tipo.toUpperCase()} generado exitosamente.\nProcede al depósito en la Bóveda.`);
}

// --- PAYMENT REPORTING LOGIC ---
const payForm = document.getElementById('paymentForm');
if (payForm) {
    payForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const data = {
            contractId: document.getElementById('pay_contract_id').value,
            month: document.getElementById('pay_month').value,
            amount: document.getElementById('pay_amount').value,
            // In a real app, we would upload the file here
            proof: "archivo_cargado_demo.pdf"
        };

        // Simulate Sending Notification
        sendPaymentNotification(data);
    });
}

function sendPaymentNotification(data) {
    const formattedAmount = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(data.amount);

    const emailSubject = `🟢 SOPORTE DE PAGO CARGADO - ${data.contractId}`;

    // DRAFT PROVIDED BY USER
    const emailBody = `
Hola, [Nombre Beneficiario].

El sistema ha recibido un comprobante de pago por valor de ${formattedAmount} correspondiente al mes de ${data.month}.

📎 [VER COMPROBANTE ADJUNTO]

⚠️ ACCIÓN REQUERIDA: Por favor verifique su cuenta bancaria.

OPCIÓN A (Todo correcto): No necesita hacer nada. Si en 48 horas no recibimos noticias suyas, el sistema marcará este mes como PAGADO automáticamente.

OPCIÓN B (No llegó el dinero): Si este recibo es falso o los fondos no entraron, tiene 48 horas para reportarlo haciendo clic en el siguiente botón rojo:

🔴 [REPORTAR FRAUDE / NO PAGO] (Link simulado: /report-fraud?id=${data.contractId})

Nota Legal: Pasadas 48 horas sin reporte, opera la Aceptación Tácita según Términos y Condiciones.
    `;

    console.log("--- SIMULANDO ENVÍO DE CORREO ---");
    console.log("Asunto:", emailSubject);
    console.log("Cuerpo:", emailBody);

    alert(`
    ✅ COMPROBANTE SUBIDO EXITOSAMENTE
    
    Hemos enviado la notificación al Beneficiario con la Regla de 48 Horas.
    
    ASUNTO: ${emailSubject}
    
    Estado: EN ESPERA DE VALIDACIÓN (48H)
    `);
}
