export const handleApiError = (error, showNotification = console.error) => {
  if (error.message === "Unauthorized" || error.message === "Token expired") {
    return;
  }

  let message = "Произошла ошибка при обращении к серверу";

  if (error.name === "TypeError" && error.message.includes("fetch")) {
    message = "Нет соединения с сервером";
  } else if (error.response) {
    switch (error.response.status) {
      case 403:
        message = "Недостаточно прав для выполнения операции";
        break;
      case 404:
        message = "Запрашиваемый ресурс не найден";
        break;
      case 500:
        message = "Внутренняя ошибка сервера";
        break;
      default:
        message = `Ошибка сервера: ${error.response.status}`;
    }
  }

  showNotification(message);
};

export const showNotification = (message, type = "error") => {
  if (type === "error") {
    console.error(message);
  } else {
    console.log(message);
  }
};
