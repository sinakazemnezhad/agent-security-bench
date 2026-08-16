def train(model, train_loader, val_loader, optimizer):
    for epoch in range(10):
        model.train()
        for batch in train_loader:
            loss = model(batch)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            for batch in val_loader:
                _ = model(batch)
        print("epoch done")
