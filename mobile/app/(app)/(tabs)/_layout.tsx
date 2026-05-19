import { View, Text, StyleSheet } from "react-native"
import { Colors } from "@/constants/design"

export default function TabsLayout() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Home (coming soon)</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bg,
    alignItems: "center",
    justifyContent: "center",
  },
  text: { color: Colors.bone, fontSize: 17 },
})
