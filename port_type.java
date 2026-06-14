// PortType.java
public final class PortType {

    private final String id;
    private final String category;
    private final String description;

    private PortType(String id, String category, String description) {
        this.id = id.toLowerCase(Locale.ROOT).trim();
        this.category = category.toUpperCase(Locale.ROOT).trim();
        this.description = description;
    }

    public String getId() { return id; }
    public String getCategory() { return category; }
    public String getDescription() { return description; }

    // Registry (same as before)
    private static final Map<String, PortType> REGISTRY = new ConcurrentHashMap<>();

    public static PortType register(String id, String category, String description) {
        PortType type = new PortType(id, category, description);
        REGISTRY.put(type.getId(), type);
        return type;
    }

    public static Optional<PortType> get(String id) {
        return Optional.ofNullable(REGISTRY.get(id.toLowerCase(Locale.ROOT)));
    }

    public static Collection<PortType> getAll() { return Collections.unmodifiableCollection(REGISTRY.values()); }
}
