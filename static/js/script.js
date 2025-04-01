document.addEventListener('DOMContentLoaded', function() {
    // Inicializar selector de fechas con Flatpickr
    const fechaConfig = {
        dateFormat: "d/m/Y",
        locale: "es",
        allowInput: true
    };
    
    flatpickr(".datepicker", fechaConfig);
    
    // Formato de números para los inputs
    const formatearNumero = (input) => {
        input.addEventListener('input', function(e) {
            // Eliminar todo excepto números
            let valor = this.value.replace(/[^\d]/g, '');
            
            // Formatear con puntos como separadores de miles
            if (valor.length > 0) {
                valor = parseInt(valor).toLocaleString('es-CO');
            }
            
            this.value = valor;
        });
    };
    
    // Aplicar formato a los campos numéricos
    formatearNumero(document.getElementById('valorContrato'));
    formatearNumero(document.getElementById('valorMensual'));
    
    // Manejar envío del formulario
    document.getElementById('calculadoraForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Mostrar spinner de carga
        document.getElementById('spinner').classList.remove('d-none');
        document.getElementById('resultadoTabla').classList.add('d-none');
        document.getElementById('resultadoResumen').classList.add('d-none');
        document.getElementById('errorAlert').classList.add('d-none');
        
        // Obtener valores del formulario
        const valorContrato = document.getElementById('valorContrato').value;
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;
        const valorMensual = document.getElementById('valorMensual').value;
        
        // Validar que las fechas tengan el formato correcto
        if (!validarFormatoFecha(fechaInicio) || !validarFormatoFecha(fechaFin)) {
            mostrarError('Por favor, ingrese las fechas en formato DD/MM/YYYY');
            return;
        }
        
        // Preparar datos para enviar al servidor
        const datos = {
            valor_contrato: valorContrato,
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
            valor_mensual: valorMensual
        };
        
        // Enviar solicitud al servidor
        fetch('/calcular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Ha ocurrido un error en el cálculo');
                });
            }
            return response.json();
        })
        .then(data => {
            // Ocultar spinner
            document.getElementById('spinner').classList.add('d-none');
            
            // Mostrar resultados
            mostrarResultados(data);
        })
        .catch(error => {
            document.getElementById('spinner').classList.add('d-none');
            mostrarError(error.message);
        });
    });
    
    // Validar formato de fecha (DD/MM/YYYY)
    function validarFormatoFecha(fecha) {
        const regex = /^\d{1,2}\/\d{1,2}\/\d{4}$/;
        return regex.test(fecha);
    }
    
    // Mostrar mensaje de error
    function mostrarError(mensaje) {
        const errorAlert = document.getElementById('errorAlert');
        errorAlert.textContent = mensaje;
        errorAlert.classList.remove('d-none');
    }
    
    // Mostrar resultados en la interfaz
    function mostrarResultados(data) {
        // Mostrar sección de resumen
        const resumen = document.getElementById('resultadoResumen');
        resumen.classList.remove('d-none');
        
        // Formatear valores para el resumen
        document.getElementById('resumenValorContrato').textContent = formatearValorMoneda(data.resumen.valor_contrato);
        document.getElementById('resumenDuracion').textContent = `${data.resumen.duracion_dias} días`;
        document.getElementById('resumenValorMensual').textContent = formatearValorMoneda(data.resumen.valor_diario * 30);
        document.getElementById('resumenValorDiario').textContent = formatearValorMoneda(data.resumen.valor_diario);
        document.getElementById('resumenTotalPagos').textContent = formatearValorMoneda(data.resumen.total_pagos);
        document.getElementById('resumenDiferencia').textContent = formatearValorMoneda(data.resumen.diferencia);
        
        // Mostrar tabla de pagos
        const tablaPagos = document.getElementById('tablaPagos');
        tablaPagos.innerHTML = '';
        
        // Llenar tabla con resultados
        data.pagos.forEach(pago => {
            const fila = document.createElement('tr');
            
            fila.innerHTML = `
                <td>${pago.Mes}</td>
                <td>${pago.Pago}</td>
                <td>${pago.Fecha_Inicio}</td>
                <td>${pago.Fecha_Fin}</td>
                <td>${pago.Dias}</td>
                <td>${formatearValorMoneda(pago.Valor_Pago)}</td>
                <td>${pago.Porcentaje}%</td>
                <td>${formatearValorMoneda(pago.Saldo_Restante)}</td>
            `;
            
            tablaPagos.appendChild(fila);
        });
        
        // Mostrar sección de tabla
        document.getElementById('resultadoTabla').classList.remove('d-none');
        
        // Hacer scroll suave hasta los resultados
        document.getElementById('resultadoTabla').scrollIntoView({ behavior: 'smooth' });
    }
    
    // Formatear valores monetarios
    function formatearValorMoneda(valor) {
        return '$' + parseFloat(valor).toLocaleString('es-CO', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
}); 