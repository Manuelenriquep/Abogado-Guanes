/**
 * CODEX GARANTÍA DIGITAL - FRONTEND LOGIC
 * Handles Calculator, Disclaimer Validation, and PDF Generation
 */

// CONFIGURATION
const COSTO_INMOBILIARIA_PCT = 1.20; // 120% of one canon (approx 10% * 12)
const COSTO_CODEX_PCT = 0.15; // 15% One time fee
const VAULT_ADDRESS = "HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH"; // Placeholder or Real if provided

const CLAUSULA_RETENCION_DEPOSITO = `CLÁUSULA DE GARANTÍA REAL Y DERECHO DE RETENCIÓN (ART. 1177 C.Co): "Las Partes acuerdan que el presente contrato se rige por las normas del DEPÓSITO MERCANTIL y servicios logísticos conexos. En consecuencia, de conformidad con el Artículo 1177 del Código de Comercio, EL OPERADOR LOGÍSTICO (Codex/Propietario) tendrá DERECHO DE RETENCIÓN sobre todas las mercancías, bienes, enseres o inventarios depositados por EL CLIENTE en el área designada.

PARÁGRAFO DE EJECUCIÓN: En caso de mora superior a 5 días en el pago de la Tarifa de Almacenaje, EL OPERADOR podrá bloquear el acceso a la bodega y retener la mercancía. Si la mora persiste por 30 días, EL CLIENTE autoriza expresamente, mediante este mandato irrevocable, la venta directa o subasta privada de las mercancías retenidas para cubrir el valor de la deuda, gastos de cobranza y costos operativos, renunciando a cualquier requerimiento judicial previo."`;

const CLAUSULA_RENUNCIA_PRIMA = `CLÁUSULA DE NATURALEZA ATÍPICA Y RENUNCIA A DERECHOS DE ARRENDAMIENTO: "Las Partes declaran expresamente que el presente vínculo jurídico corresponde a un CONTRATO DE CONCESIÓN DE ESPACIO COMERCIAL (Coworking/Pop-Up) y no a un arrendamiento de local comercial. La causa del contrato es la prestación de servicios integrales (Seguridad, Marketing del Centro, Aseo, Conectividad) donde el espacio físico es meramente instrumental.

RENUNCIA EXPRESA: En virtud de la autonomía de la voluntad y la naturaleza atípica de este contrato, EL CONCESIONARIO (Ocupante) manifiesta conocer que NO LE SON APLICABLES las disposiciones de los Artículos 518 a 524 del Código de Comercio. En consecuencia, RENUNCIA expresamente a reclamar:

1. Derecho a la renovación automática del contrato.
2. Prima comercial o 'Goodwill' por acreditación del establecimiento.
3. Indemnizaciones por terminación unilateral o no renovación al vencimiento del plazo pactado."`;

const CLAUSULA_GESTION_REMOTA = `CLÁUSULA DE MANDATO DE GESTIÓN REMOTA: "EL PROPIETARIO declara conocer que el servicio prestado por CODEX ANALÍTICA es de naturaleza Tecnológica, Financiera y Jurídica. En consecuencia, CODEX ANALÍTICA NO asume obligaciones de mandatario general sobre el cuidado material del inmueble.

Quedan expresamente excluidas del mandato:

1. Visitas de inspección ocular o inventarios físicos.
2. Gestión de llaves, reparaciones, aseo o mantenimiento.
3. Atención de emergencias locativas (plomería, electricidad, etc.). EL PROPIETARIO conserva la guarda material del bien y libera a CODEX de cualquier responsabilidad por deterioro físico del inmueble."`;

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
// --- FORM & PDF GENERATION ---
function toggleServices() {
    const tipo = document.getElementById('k_tipo_uso').value;
    const serviciosDiv = document.getElementById('servicios-conexos');
    if (tipo === 'comercio') {
        serviciosDiv.style.display = 'block';
    } else {
        serviciosDiv.style.display = 'none';
        // Uncheck all if hidden to avoid confusion
        document.querySelectorAll('input[name="servicios"]').forEach(el => el.checked = false);
    }
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

        const tipoUso = document.getElementById('k_tipo_uso').value;
        let serviciosSeleccionados = [];

        // Validate Services for Comercio
        if (tipoUso === 'comercio') {
            const checkboxes = document.querySelectorAll('input[name="servicios"]:checked');
            if (checkboxes.length === 0) {
                alert("Para Concesión Comercial, debes seleccionar al menos un servicio conexo.");
                return;
            }
            checkboxes.forEach((checkbox) => {
                serviciosSeleccionados.push(checkbox.value);
            });
        }

        // Get Data
        const data = {
            tipo: tipoUso,
            servicios: serviciosSeleccionados.join(', '),
            nombre: document.getElementById('k_nombre').value,
            cedula: document.getElementById('k_cedula').value,
            telefono: document.getElementById('k_telefono').value,
            email: document.getElementById('k_email').value,
            ciudad: document.getElementById('k_ciudad').value
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

    if (data.tipo === 'vivienda') {
        title = "CONTRATO DE HOSPEDAJE MERCANTIL";
        bodyText = `
    Ciudad de Firma: ${data.ciudad}
    
    Entre los suscritos a saber: POR UNA PARTE, CODEX ANALÍTICA S.A.S (en adelante EL OPERADOR), y POR OTRA PARTE, ${data.nombre} identificado con C.C. ${data.cedula} (en adelante EL HUÉSPED), hemos convenido celebrar el presente CONTRATO DE HOSPEDAJE MERCANTIL, regido por las siguientes cláusulas:

    PRIMERA. NATURALEZA: El presente contrato se rige estrictamente por las normas del Código de Comercio (Arts. 1192 y ss) y NO constituye arrendamiento de vivienda urbana confome a la Ley 820 de 2003.

    SEGUNDA. ${CLAUSULA_GESTION_REMOTA}

    TERCERA. GARANTÍA DIGITAL: El HUÉSPED constituye una garantía mediante depósito de activos digitales en la Bóveda Multisig designada por EL OPERADOR.

    CUARTA. CESIÓN DE FRUTOS: El HUÉSPED cede expresamente a favor de EL OPERADOR cualquier rendimiento, staking reward, yield o interés generado por los activos digitales depositados como garantía, como contraprestación por los servicios de gestión tecnológica y custodia segura.

    QUINTA. DERECHO DE RETENCIÓN: En caso de impago del canon de hospedaje, EL OPERADOR podrá ejercer el derecho de retención sobre los bienes del HUÉSPED y ejecutar la garantía digital de forma inmediata.

    SEXTA. PENALIDAD POR SERVICIOS: El HUÉSPED autoriza el descuento automático de la garantía para cubrir servicios públicos o expensas impagas al momento de la restitución.
        `;
    } else if (data.tipo === 'bodega') {
        title = "CONTRATO DE DEPÓSITO Y SERVICIOS LOGÍSTICOS";
        bodyText = `
    Ciudad de Firma: ${data.ciudad}

    Entre los suscritos, CODEX ANALÍTICA S.A.S (EL DEPOSITARIO) y ${data.nombre} con Nit/CC ${data.cedula} (EL DEPOSITANTE), celebran este CONTRATO DE DEPÓSITO MERCANTIL:

    PRIMERA. OBJETO: El DEPOSITARIO se obliga a recibir las mercancías del DEPOSITANTE para su guarda y custodia en el espacio asignado. NO EXISTE ARRENDAMIENTO de inmueble, sino prestación de servicios de bodegaje.

    SEGUNDA. ${CLAUSULA_GESTION_REMOTA}

    TERCERA. TARIFA DE ALMACENAJE: El pago mensual corresponde exclusivamente a la tarifa de custodia y administración logística.

    CUARTA. ${CLAUSULA_RETENCION_DEPOSITO}

    QUINTA. GARANTÍA Y YIELD: La garantía digital depositada generará rendimientos financieros que son cedidos en su totalidad al DEPOSITARIO como remuneración parcial por la gestión de la billetera de seguridad.
        `;
    } else if (data.tipo === 'comercio') {
        title = "CONTRATO DE CONCESIÓN DE ESPACIO COMERCIAL";
        bodyText = `
    Ciudad de Firma: ${data.ciudad}

    Entre CODEX ANALÍTICA S.A.S (EL CONCEDENTE) y ${data.nombre} con Nit/CC ${data.cedula} (EL CONCESIONARIO), acuerdan:

    PRIMERA. ${CLAUSULA_RENUNCIA_PRIMA}

    SEGUNDA. ${CLAUSULA_GESTION_REMOTA}

    TERCERA. SERVICIOS CONEXOS: El contrato incluye indivisiblemente los servicios de: ${data.servicios}, justificando la naturaleza de concesión comercial y no de tenencia simple.

    CUARTA. GARANTÍA MULTISIG: El incumplimiento en el pago del canon de concesión activará la ejecución inmediata de la garantía digital custodiada en Sqauds Multisig.
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
    const fullText = bodyText + `\n\nFirmado digitalmente el ${dateStr}.`;

    const splitText = doc.splitTextToSize(fullText, pageWidth);
    doc.text(splitText, margin, y);

    // SIGNATURE MOCKUP
    y += (splitText.length * lineHeight) + 20;
    doc.text("__________________________", margin, y);
    doc.text(`Firma: ${data.nombre}`, margin, y + 10);
    doc.text(`ID: ${data.cedula}`, margin, y + 15);

    // SAVE
    doc.save(`Contrato_${data.tipo}_${data.cedula}.pdf`);

    alert(`Contrato de ${data.tipo.toUpperCase()} generado exitosamente.\nProcede al depósito en la Bóveda.`);
}
