/**
 * 管理后台JavaScript功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化管理后台功能
    initAdminFeatures();
});

/**
 * 初始化管理后台功能
 */
function initAdminFeatures() {
    // 添加表格行悬停效果
    enhanceTableHover();
    
    // 添加删除确认增强
    enhanceDeleteConfirmation();
    
    // 添加统计卡片动画
    animateStatCards();
    
    // 添加响应式表格
    makeTablesResponsive();
    
    // 添加页面加载动画
    addPageLoadAnimation();
}

/**
 * 增强表格行悬停效果
 */
function enhanceTableHover() {
    const tables = document.querySelectorAll('.admin-table');
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.01)';
                this.style.transition = 'transform 0.2s ease';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    });
}

/**
 * 增强删除确认功能
 */
function enhanceDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('.btn-admin-danger');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // 已经通过onclick属性设置了确认对话框，这里可以添加额外的逻辑
            const buttonText = this.textContent.trim();
            const isConfirmed = confirm(this.getAttribute('onclick').match(/'([^']+)'/)[1]);
            
            if (!isConfirmed) {
                e.preventDefault();
                return false;
            }
            
            // 添加删除动画效果
            this.style.opacity = '0.5';
            this.innerHTML = '🗑️ 删除中...';
            this.disabled = true;
            
            // 提交表单
            const form = this.closest('form');
            if (form) {
                setTimeout(() => {
                    form.submit();
                }, 300);
            }
        });
    });
}

/**
 * 统计卡片动画
 */
function animateStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        // 延迟动画
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100);
        }, index * 100);
    });
    
    // 数字递增动画
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(number => {
        const finalValue = parseInt(number.textContent);
        let currentValue = 0;
        const increment = Math.ceil(finalValue / 20);
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                number.textContent = finalValue;
                clearInterval(timer);
            } else {
                number.textContent = currentValue;
            }
        }, 50);
    });
}

/**
 * 使表格响应式
 */
function makeTablesResponsive() {
    const tables = document.querySelectorAll('.admin-table');
    
    tables.forEach(table => {
        // 添加表格包装器以实现响应式滚动
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        wrapper.style.overflowX = 'auto';
        wrapper.style.marginTop = '1rem';
        
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
        
        // 添加表格标题行固定
        const thead = table.querySelector('thead');
        if (thead) {
            thead.style.position = 'sticky';
            thead.style.top = '0';
            thead.style.zIndex = '10';
            thead.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    });
}

/**
 * 页面加载动画
 */
function addPageLoadAnimation() {
    const adminMain = document.querySelector('.admin-main');
    if (adminMain) {
        adminMain.style.opacity = '0';
        adminMain.style.transform = 'translateY(20px)';
        adminMain.style.transition = 'all 0.5s ease';
        
        setTimeout(() => {
            adminMain.style.opacity = '1';
            adminMain.style.transform = 'translateY(0)';
        }, 100);
    }
}

/**
 * 添加搜索功能（可选）
 */
function addSearchFunctionality() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = '🔍 搜索用户、故事或讨论...';
    searchInput.className = 'admin-search';
    searchInput.style.cssText = `
        width: 100%;
        max-width: 300px;
        padding: 0.75rem 1rem;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    `;
    
    searchInput.addEventListener('focus', function() {
        this.style.borderColor = '#667eea';
        this.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
    });
    
    searchInput.addEventListener('blur', function() {
        this.style.borderColor = '#e2e8f0';
        this.style.boxShadow = 'none';
    });
    
    // 将搜索框添加到合适的位置
    const adminHeaders = document.querySelectorAll('.admin-header');
    if (adminHeaders.length > 0) {
        adminHeaders[0].appendChild(searchInput);
    }
}

/**
 * 添加批量操作功能（可选）
 */
function addBatchOperations() {
    const tables = document.querySelectorAll('.admin-table');
    
    tables.forEach(table => {
        // 添加复选框到每行
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const checkboxCell = document.createElement('td');
            checkboxCell.style.width = '40px';
            checkboxCell.style.textAlign = 'center';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'row-checkbox';
            checkbox.style.cssText = `
                width: 18px;
                height: 18px;
                cursor: pointer;
            `;
            
            checkboxCell.appendChild(checkbox);
            row.insertBefore(checkboxCell, row.firstChild);
        });
        
        // 添加表头复选框
        const headerRow = table.querySelector('thead tr');
        if (headerRow) {
            const headerCheckboxCell = document.createElement('th');
            headerCheckboxCell.style.width = '40px';
            headerCheckboxCell.style.textAlign = 'center';
            
            const headerCheckbox = document.createElement('input');
            headerCheckbox.type = 'checkbox';
            headerCheckbox.className = 'select-all-checkbox';
            headerCheckbox.style.cssText = `
                width: 18px;
                height: 18px;
                cursor: pointer;
            `;
            
            headerCheckbox.addEventListener('change', function() {
                const rowCheckboxes = table.querySelectorAll('.row-checkbox');
                rowCheckboxes.forEach(cb => cb.checked = this.checked);
            });
            
            headerCheckboxCell.appendChild(headerCheckbox);
            headerRow.insertBefore(headerCheckboxCell, headerRow.firstChild);
        }
    });
}

/**
 * 添加键盘快捷键支持
 */
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + / 显示快捷键帮助
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcuts();
        }
        
        // Ctrl + S 保存（如果有表单）
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const forms = document.querySelectorAll('form');
            if (forms.length > 0) {
                forms[0].submit();
            }
        }
    });
}

/**
 * 显示键盘快捷键帮助
 */
function showKeyboardShortcuts() {
    const shortcuts = [
        { key: 'Ctrl + /', description: '显示快捷键帮助' },
        { key: 'Ctrl + S', description: '保存表单' },
        { key: 'Tab', description: '在表单元素间切换' },
        { key: 'Enter', description: '提交表单或点击按钮' }
    ];
    
    let shortcutsHTML = '<div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); z-index: 1000; max-width: 400px;">';
    shortcutsHTML += '<h3 style="margin-bottom: 1rem; color: #2d3748;">⌨️ 键盘快捷键</h3>';
    shortcutsHTML += '<div style="margin-bottom: 1rem;">';
    
    shortcuts.forEach(shortcut => {
        shortcutsHTML += `<div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; padding: 0.5rem; background: #f7fafc; border-radius: 4px;">`;
        shortcutsHTML += `<span style="font-weight: 600; color: #667eea;">${shortcut.key}</span>`;
        shortcutsHTML += `<span style="color: #4a5568;">${shortcut.description}</span>`;
        shortcutsHTML += `</div>`;
    });
    
    shortcutsHTML += '</div>';
    shortcutsHTML += '<button onclick="this.parentElement.remove()" style="width: 100%; padding: 0.75rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">关闭</button>';
    shortcutsHTML += '</div>';
    shortcutsHTML += '<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999;" onclick="this.nextElementSibling.remove(); this.remove();"></div>';
    
    document.body.insertAdjacentHTML('beforeend', shortcutsHTML);
}

// 初始化高级功能（可选，根据需求启用）
function initAdvancedFeatures() {
    // 启用搜索功能
    addSearchFunctionality();
    
    // 启用批量操作
    addBatchOperations();
    
    // 启用键盘快捷键
    addKeyboardShortcuts();
}

// 页面加载完成后初始化高级功能
setTimeout(initAdvancedFeatures, 1000);