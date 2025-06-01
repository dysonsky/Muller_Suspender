# Add this to the HTML_TEMPLATE section (around line 100)
"""
<div class="panel" style="text-align: center; background: #f8f9fa;">
    <h3>📌 OWNER MENU (LOCKED)</h3>
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 15px;">
        <button class="btn" style="background: #6c757d; cursor: not-allowed;" title="Contact Owner" onclick="alert('Owner: MULLER SUSPENDER\nNumber: +254705101667')">
            👑 OWNER KING
        </button>
        <button class="btn" style="background: #6c757d; cursor: not-allowed;" title="Purchase Script" onclick="alert('Contact owner to purchase script\n+254705101667')">
            💰 BUY SCRIPT
        </button>
        <button class="btn" style="background: #6c757d; cursor: not-allowed;" title="Direct Contact" onclick="alert('WhatsApp Owner: +254705101667\nName: MULLER SUSPENDER')">
            📞 CONTACT BOT OWNER
        </button>
    </div>
    <p style="color: #6c757d; margin-top: 10px; font-size: 0.9em;">
        These buttons are locked and cannot be modified
    </p>
</div>
"""

# And add this CSS to the style section (around line 30)
"""
.btn:disabled, .btn[disabled] {
    opacity: 1;
    cursor: not-allowed !important;
}
.owner-menu {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e6e9 100%);
    border: 1px solid #d1d5db;
}
"""
