const addEventListenerMulti = (collection, event, handler) => {
    Array.from(collection).forEach(t => t.addEventListener(event, handler));
}