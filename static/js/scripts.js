// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 添加表单提交确认
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // 简单的表单验证
            const inputs = this.querySelectorAll('input[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'red';
                } else {
                    input.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('请填写所有必填字段');
            }
        });
    });
    
    // 添加平滑滚动效果
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 高亮当前活动的导航链接
    const currentUrl = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        const linkUrl = new URL(link.href).pathname;
        if (currentUrl === linkUrl) {
            link.style.fontWeight = 'bold';
            link.style.textDecoration = 'underline';
        }
    });
    
    // 添加章节评论区的展开/折叠功能
    const chapterComments = document.querySelectorAll('.chapter-comments');
    chapterComments.forEach(commentSection => {
        const h5 = commentSection.querySelector('h5');
        const comments = commentSection.querySelector('ul');
        const form = commentSection.querySelector('form');
        
        if (h5 && comments && form) {
            h5.style.cursor = 'pointer';
            let isOpen = true;
            
            h5.addEventListener('click', function() {
                isOpen = !isOpen;
                if (isOpen) {
                    comments.style.display = 'block';
                    form.style.display = 'block';
                } else {
                    comments.style.display = 'none';
                    form.style.display = 'none';
                }
            });
        }
    });
});