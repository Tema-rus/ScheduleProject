document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.institute-name').forEach(institute => {
        institute.addEventListener('click', () => {
            const courses = institute.nextElementSibling;
            const isOpen = courses.classList.contains('open');

            document.querySelectorAll('.courses').forEach(course => {
                course.classList.remove('open');
            });
            document.querySelectorAll('.groups').forEach(group => {
                group.classList.remove('open');
            });

            if (!isOpen) {
                courses.classList.add('open');
            }
        });
    });

    document.querySelectorAll('.course-name').forEach(course => {
        course.addEventListener('click', (e) => {
            const groups = course.nextElementSibling;  // Список групп
            const courseContainer = course.closest('.course');  // Контейнер для текущего курса
            const isOpen = groups.classList.contains('open');

            const allCourses = courseContainer.closest('.institute').querySelectorAll('.groups');
            allCourses.forEach(group => {
                group.classList.remove('open');
            });

            if (!isOpen) {
                groups.classList.add('open');
            }

            e.stopPropagation();
        });
    });
});

$(document).ready(function () {
    let debounceTimeout;

    // Обработчик ввода текста в поле поиска
    $('#search-input').on('input', function () {
        clearTimeout(debounceTimeout);

        const query = $(this).val().trim();

        if (query.length > 0) {
            debounceTimeout = setTimeout(function() {
                $.get('/search_suggestions/', { query: query }, function (data) {
                    if (data.groups.length > 0 || data.teachers.length > 0) {
                        let suggestionsHtml = '';

                        data.groups.forEach(function (group) {
                            suggestionsHtml += `<li class="suggestion-item"><a href="/groups/${group.slug}">${group.name}</a></li>`;
                        });

                        data.teachers.forEach(function (teacher) {
                            suggestionsHtml += `<li class="suggestion-item"><a href="/teachers/${teacher.slug}">${teacher.name}</a></li>`;
                        });

                        $('#suggestions-list').html(suggestionsHtml).show();
                    } else {
                        $('#suggestions-list').hide();
                    }
                });
            }, 300); // 300ms задержка
        } else {
            $('#suggestions-list').hide();
        }
    });
});

