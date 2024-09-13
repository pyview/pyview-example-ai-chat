document.body.addEventListener('click', function (e) {
    // Check if the clicked element is the ::before pseudo-element of a pre block
    if (e.target.closest('pre')) {
        const pre = e.target.closest('pre'); // Get the closest pre element
        const code = pre.querySelector('code')?.textContent;
        if (code) {
            navigator.clipboard.writeText(code).then(() => {
                pre.classList.add('copied');

                // After 2 seconds, change it back to "Copy code"
                setTimeout(() => {
                    pre.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Error copying text: ', err);
            });
        }
    }
});