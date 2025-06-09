async function postJSON(url, data) {
    const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return resp.json();
}

function formHandler(formId, handler) {
    document.getElementById(formId).addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const data = Object.fromEntries(new FormData(form).entries());
        try {
            const result = await handler(data);
            document.getElementById(formId.replace('Form', 'Result')).textContent = JSON.stringify(result, null, 2);
        } catch (err) {
            document.getElementById(formId.replace('Form', 'Result')).textContent = err.toString();
        }
    });
}

formHandler('designForm', (d) => postJSON('/v1/design-jobs', { project_id: d.project_id, preview_only: d.preview_only === 'on' }));
formHandler('statusForm', async (d) => {
    const resp = await fetch(`/v1/design-jobs/${d.job_id}`);
    return resp.json();
});
formHandler('purchaseForm', (d) => postJSON('/v1/credits/purchase', d));
formHandler('deductForm', (d) => postJSON('/v1/credits/deduct', { tenant_id: d.tenant_id, amount: Number(d.amount) }));
formHandler('rateForm', async (d) => {
    const resp = await fetch(`/v1/rate-card?tenant_id=${encodeURIComponent(d.tenant_id)}`);
    return resp.json();
});
