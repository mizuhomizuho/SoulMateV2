document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.js-s4__res-btn').forEach((el) => {
        el.addEventListener('click', (e) => {
            const boxEl = e.currentTarget.closest('.js-s4__el-box')
            boxEl.style.backgroundColor = 'rgba(255, 255, 255, .1)'
            boxEl.style.borderRadius = '8px'
            boxEl.querySelector('tbody').style.visibility = 'hidden'
            const pk = boxEl.dataset.id
            const act = e.currentTarget.dataset.act
            const success = (data) => {
                if (data === false || data.res !== true) {
                    alert('Не удалось выполнить операцию')
                }
            }
            fetch('/catalog/set-s4res/' + pk + '/' + act + '/')
            .then(response => response.json())
            .catch(error => success(false))
            .then(data => success(data))
        })
    })
})