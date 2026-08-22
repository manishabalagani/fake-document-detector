const User = require("./User");
const Document = require("./Document");
const Analysis = require("./Analysis");

// User -> Documents
User.hasMany(Document, {
    foreignKey: "userId",
    onDelete: "CASCADE"
});

Document.belongsTo(User, {
    foreignKey: "userId"
});

// Document -> Analysis
Document.hasOne(Analysis, {
    foreignKey: "documentId",
    onDelete: "CASCADE"
});

Analysis.belongsTo(Document, {
    foreignKey: "documentId"
});

module.exports = {
    User,
    Document,
    Analysis
};