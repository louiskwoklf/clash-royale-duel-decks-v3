document.addEventListener('DOMContentLoaded', function() {
    let selectedDeck = null;
    const bannedContainer = document.getElementById('banned-cards-container');
    let bannedMode = false;
    bannedContainer.addEventListener('click', function(e) {
      if(e.target.tagName.toLowerCase() === 'img') {
        // If a banned card image is clicked, remove it and un-grey the corresponding card button
        e.stopPropagation();
        const cardName = e.target.getAttribute('alt');
        e.target.remove();
        const cardButton = document.querySelector(`.card-button[data-card="${cardName}"]`);
        if(cardButton) cardButton.classList.remove('banned');
      } else {
        // Toggle banned mode when clicking on the container background
        bannedContainer.classList.toggle('active');
        bannedMode = bannedContainer.classList.contains('active');
        if (bannedMode) {
          // Deselect any selected deck
          document.querySelectorAll('.deck.selected-deck').forEach(deck => deck.classList.remove('selected-deck'));
          selectedDeck = null;
        }
      }
    });
  
    const decks = document.querySelectorAll('.deck:not(.read-only)');
    decks.forEach(deck => {
      deck.addEventListener('click', function() {
        if (bannedContainer.classList.contains('active')) {
          bannedContainer.classList.remove('active');
          bannedMode = false;
        }
        if (deck.classList.contains('selected-deck')) {
          deck.classList.remove('selected-deck');
          if (selectedDeck === deck) selectedDeck = null;
        } else {
          decks.forEach(d => d.classList.remove('selected-deck'));
          deck.classList.add('selected-deck');
          selectedDeck = deck;
        }
      });
    });
  
    const cardButtons = document.querySelectorAll('.card-button');
    cardButtons.forEach(button => {
      button.addEventListener('click', function() {
        const cardName = button.getAttribute("data-card");
        if(bannedMode) {
          if(button.classList.contains("banned")) {
            const bannedImg = bannedContainer.querySelector(`img[alt="${cardName}"]`);
            if(bannedImg) bannedImg.remove();
            button.classList.remove("banned");
          } else {
            const img = button.querySelector('img');
            if(img) {
              const bannedImg = img.cloneNode(true);
              bannedContainer.appendChild(bannedImg);
              button.classList.add("banned");
            }
          }
          return;
        }
        if (button.classList.contains("used")) {
          const deckImg = document.querySelector(`.deck:not(.read-only) .deck-slot img[alt="${cardName}"]`);
          if (deckImg) deckImg.parentElement.innerHTML = "";
          button.classList.remove("used");
          return;
        }
        if (!selectedDeck) {
          alert('Please select a deck first.');
          return;
        }
        const slots = selectedDeck.querySelectorAll('.deck-slot');
        let emptySlot = null;
        for (let slot of slots) {
          if (!slot.querySelector('img')) {
            emptySlot = slot;
            break;
          }
        }
        if (!emptySlot) {
          alert('The selected deck is already full.');
          return;
        }
        const img = button.querySelector('img');
        if (img) {
          const cardImg = img.cloneNode(true);
          emptySlot.innerHTML = '';
          emptySlot.appendChild(cardImg);
          button.classList.add('used');
        }
      });
    });
  
    const deckSlots = document.querySelectorAll('.deck:not(.read-only) .deck-slot');
    deckSlots.forEach(slot => {
      slot.addEventListener('click', function(e) {
        const img = slot.querySelector('img');
        if (img) {
          e.stopPropagation();
          const cardName = img.getAttribute('alt');
          slot.innerHTML = '';
          const cardButton = document.querySelector(`.card-button[data-card="${cardName}"]`);
          if (cardButton) cardButton.classList.remove('used');
        }
      });
    });
  
    const clearDeckButtons = document.querySelectorAll('.clear-deck');
    clearDeckButtons.forEach(btn => {
      btn.addEventListener('click', function() {
        const deckIndex = btn.getAttribute('data-deck-index');
        const deckEl = document.querySelector(`.deck[data-deck-index="${deckIndex}"]`);
        deckEl.querySelectorAll('img').forEach(img => {
          const cardName = img.getAttribute('alt');
          const cardButton = document.querySelector(`.card-button[data-card="${cardName}"]`);
          if (cardButton) cardButton.classList.remove('used');
        });
        deckEl.querySelectorAll('.deck-slot').forEach(slot => slot.innerHTML = '');
      });
    });
  
    document.querySelector('.clear-all-decks').addEventListener('click', function() {
      document.querySelectorAll('.deck:not(.read-only)').forEach(deckEl => {
        deckEl.querySelectorAll('img').forEach(img => {
          const cardName = img.getAttribute('alt');
          const cardButton = document.querySelector(`.card-button[data-card="${cardName}"]`);
          if (cardButton) cardButton.classList.remove('used');
        });
        deckEl.querySelectorAll('.deck-slot').forEach(slot => slot.innerHTML = '');
      });
    });
  
    document.querySelector('.clear-banned-cards').addEventListener('click', function() {
      const bannedImages = bannedContainer.querySelectorAll('img');
      bannedImages.forEach(function(img) {
        const cardName = img.getAttribute('alt');
        const cardButton = document.querySelector(`.card-button[data-card="${cardName}"]`);
        if(cardButton) cardButton.classList.remove('banned');
        img.remove();
      });
    });
  
    document.querySelector('.search-button').addEventListener('click', function() {
      for (let i = 0; i < 4; i++) {
        const deckEl = document.querySelector(`.deck[data-deck-index="${i}"]`);
        const images = deckEl.querySelectorAll('img');
        let cardNames = [];
        images.forEach(img => cardNames.push(img.alt));
        document.getElementById(`deck${i}`).value = cardNames.join(',');
      }
      const bannedImages = bannedContainer.querySelectorAll('img');
      let bannedCardNames = [];
      bannedImages.forEach(img => bannedCardNames.push(img.alt));
      document.getElementById('banned_cards').value = bannedCardNames.join(',');
    });
});