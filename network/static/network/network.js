document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-btn').forEach(button => {
        button.onclick = function() {
            const postId = this.dataset.id;
            fetch(`/post/${postId}/like`, {
                method: 'PUT',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    console.log(result.error);
                } else {
                    document.querySelector(`#like-count-${postId}`).innerHTML = result.likes_count;
                    if (result.action === 'liked') {
                        this.innerHTML = 'Unlike 💔';
                    } else {
                        this.innerHTML = 'Like ❤️';
                    }
                }
            });
        };
    });

    document.querySelectorAll('.edit-btn').forEach(button => {
        button.onclick = function() {
            const postId = this.dataset.id;
            const contentP = document.querySelector(`#post-content-${postId}`);
            const originalContent = contentP.innerHTML;

            this.style.display = 'none';

            const textarea = document.createElement('textarea');
            textarea.className = 'form-control mb-2';
            textarea.value = originalContent;

            const saveBtn = document.createElement('button');
            saveBtn.className = 'btn btn-primary btn-sm save-btn';
            saveBtn.innerHTML = 'Save';

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'btn btn-secondary btn-sm ml-2';
            cancelBtn.innerHTML = 'Cancel';

            contentP.innerHTML = '';
            contentP.appendChild(textarea);
            contentP.appendChild(saveBtn);
            contentP.appendChild(cancelBtn);

            saveBtn.onclick = function() {
                const newContent = textarea.value;
                fetch(`/post/${postId}/edit`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        content: newContent
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.error) {
                        console.log(result.error);
                    } else {
                        contentP.innerHTML = result.content;
                        button.style.display = 'inline-block';
                    }
                });
            };

            cancelBtn.onclick = function() {
                contentP.innerHTML = originalContent;
                button.style.display = 'inline-block';
            };
        };
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
