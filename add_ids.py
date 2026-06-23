import re

with open('templates/payslip_designer.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Add IDs to the right side template
c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Month]</span></div>',
    '<div class="drop-target" id="tpl-month" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Month]</span></div>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Days]</span></div>',
    '<div class="drop-target" id="tpl-paid-days" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Days]</span></div>'
)

c = c.replace(
    '<div contenteditable="true" style="width: 25%; padding: 5px; text-align:right;">0</div>',
    '<div id="tpl-cl-bal" contenteditable="true" style="width: 25%; padding: 5px; text-align:right;">0</div>', 1
)

c = c.replace(
    '<div contenteditable="true" style="width: 25%; padding: 5px; text-align:right;">0</div>',
    '<div id="tpl-el-bal" contenteditable="true" style="width: 25%; padding: 5px; text-align:right;">0</div>', 1
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 10px;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Earning Labels]</span>',
    '<div class="drop-target" id="tpl-earn-lbls" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 10px;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Earning Labels]</span>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 10px; text-align:right;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Amounts]</span>',
    '<div class="drop-target" id="tpl-earn-amts" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 10px; text-align:right;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Amounts]</span>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 10px;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Deduction Labels]</span>',
    '<div class="drop-target" id="tpl-ded-lbls" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 10px;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Deduction Labels]</span>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; padding: 10px; text-align:right;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Amounts]</span>',
    '<div class="drop-target" id="tpl-ded-amts" contenteditable="true" style="width: 25%; padding: 10px; text-align:right;">\n                                <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Drop Amounts]</span>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Earnings Total]</span></div>',
    '<div class="drop-target" id="tpl-earn-total" contenteditable="true" style="width: 25%; border-right: 1px solid #000; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Earnings Total]</span></div>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Deductions Total]</span></div>',
    '<div class="drop-target" id="tpl-ded-total" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Deductions Total]</span></div>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; font-weight:bold; font-size:14px; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Net Pay Amount]</span></div>',
    '<div class="drop-target" id="tpl-net-pay" contenteditable="true" style="width: 25%; padding: 5px; text-align:right; font-weight:bold; font-size:14px; min-height: 25px;"><span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Net Pay Amount]</span></div>'
)

c = c.replace(
    '<div class="drop-target" contenteditable="true" style="border-left: 1px solid #000; border-right: 1px solid #000; padding: 5px; font-weight:bold; text-align:right; font-size:14px; min-height: 25px;">\n                            <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Amount in Words]</span>',
    '<div class="drop-target" id="tpl-amt-words" contenteditable="true" style="border-left: 1px solid #000; border-right: 1px solid #000; padding: 5px; font-weight:bold; text-align:right; font-size:14px; min-height: 25px;">\n                            <span class="placeholder-text" style="color:#aaa; pointer-events:none;">[Amount in Words]</span>'
)

c = c.replace(
    '<span class="drop-target placeholder-text" style="color:#aaa; pointer-events:none; display:inline-block; min-width:80px; min-height:16px;">[Payment Date]</span>',
    '<span class="drop-target placeholder-text" id="tpl-pay-date" style="color:#aaa; pointer-events:none; display:inline-block; min-width:80px; min-height:16px;">[Payment Date]</span>'
)

with open('templates/payslip_designer.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("done")
